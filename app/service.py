import serial, socket, threading
import time, random, json, array
import os, sys, logging
from app import helpers, so

class Service():

    def __init__(self, config):
        self.config = config
        self.first_request = None
        self.node_sevice = None
        self.discover_service = None

    def activateDiscoverService(self):
        self.discover_service = DiscoverService(self.config)
        self.discover_service.start()
    
    def activateNodeService(self):
        self.node_sevice = NodeService(self.config)
        self.node_sevice.start()

class DiscoverService(threading.Thread):

    def __init__(self, config):
        self.config = config
        threading.Thread.__init__(self)

    def run(self):
        logging.info('Starting the discover service')
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            message = "s-hostname:%s" % socket.gethostname()
            sock.sendto(message.encode(), (self.config.BROADCAST_MASK, self.config.BROADCAST_PORT))
            time.sleep(self.config.BROADCAST_INTERVAL)

class NodeService(threading.Thread):

    nodes = {}

    def __init__(self, config):
        self.config = config
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config.SOCKET_BIND_ADDRESS, self.config.SOCKET_BIND_PORT))        
        sock.listen(self.config.SOCKET_CONNECTIONS)

        while True:
            conn, addr = sock.accept()
            node = RpiNode(self, conn, addr)
            node.start()

    def addNode(self, node):
        db_session = self.config.getNewDbSession()
        nh = helpers.NodeHelper(db_session)
        host_name = node.hostname
        logging.info('try to add node %s' % host_name)
        
        if host_name in self.nodes:
            db_session.close()
            return False

        db_node = nh.getNodeByName(host_name)

        if db_node == None:
            logging.info('try to create a node with name %s' % host_name)
            if nh.createNode({'name': None, 'host_name': host_name, 'order': None}) == None:
                db_session.close()
                return False
            so.emit('updateNodes', {'nodes': nh.getNodes()}, broadcast=True)
        elif db_node == False:
            logging.error('Fail to create a node')
            db_session.close()
            return False
        else:
            logging.info('Node found in DB')

        self.nodes[host_name] = node
        db_session.close()
        return True

    def pushToNode(self, event):
        if event['host_name'] in self.nodes:
            logging.info('pushing')
            node = self.nodes[event['host_name']].sendEvent(event)
            return True
        else:
            logging.warning('no node')
            return False

    def removeNode(self, hostname):
        logging.info('try to delete %s' % hostname)
        if hostname in self.nodes:
            del self.nodes[hostname]
            logging.info('delete successuful %s' % hostname)

class RpiNode(threading.Thread):

    def __init__(self, service, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.hostname = None
        self.service = service

    def getHostName(self):
        return self.hostname

    def sendEvent(self, event):
        try:
            data = "%s\n" % json.dumps(event)
            self.conn.send(data.encode())
        except Exception as e:
            logging.warning('Fail to send event to rpi node')
            # self.service.removeNode(self.hostname)
            # self.conn.close()

    def run(self):
        logging.info('New connection from %s' % self.addr[0])
        message_buff = ''

        while True:
            try:
                data = self.conn.recv(1)
                if data:
                    udata = data.decode()

                    if udata != "\n":
                        message_buff += udata
                        continue

                    if self.hostname == None:
                        splited_data = message_buff.split(':')

                        if splited_data[1] and splited_data[1] == 'handshake':
                            self.hostname = splited_data[0]
                            
                            if self.service.addNode(self) == False:
                                logging.warning('Could not add the node')
                                self.conn.close()
                                break;

                            handshake = 'accept'
                            self.conn.send(handshake.encode())
                    else:
                        db_session = self.service.config.getNewDbSession()
                        sp = SocketParser(self, db_session, message_buff)
                        sp.run()
                        db_session.close()

                    message_buff = ''
                else:
                    logging.info('Connection closed for %s' % self.addr[0])
                    # self.service.removeNode(self.hostname)
                    # self.conn.close()
                    break
            except Exception as e:
                logging.error('Socket error, close connection')
                logging.error(e)
                # self.service.removeNode(self.hostname)
                # self.conn.close()
                break

        self.service.removeNode(self.hostname)
        self.conn.close()
        # self.db_session.close()

class SocketParser():

    def __init__(self, rpi_node, db_session, data):
        # threading.Thread.__init__(self)
        self.hostname = rpi_node.hostname
        self.data = data
        self.service = rpi_node.service
        self.db_session = db_session
        
    def run(self):
        try:
            data = json.loads(self.data)
        except ValueError as e:
            logging.debug(self.data)
            logging.error('Broken json from socket')
            return

        data = json.loads(self.data)

        if 'type' in data and data['type'] == 'response':
            logging.debug('%s received: %s' % (self.hostname, self.data))
        elif 'type' in data and data['type'] == 'event':
            params = {}
            tags = {'hostname': self.hostname}

            if 'port' in data:
                tags['port'] = data['port']

            if 'radio_pipe' in data:
                tags['radio_pipe'] = data['radio_pipe']
            
            if data['result'] == 'success':
                try:
                    if 'h' in data['message']:
                        params['humiValue'] = float(data['message']['h'])
                    if 't' in data['message']:
                        params['tempValue'] = float(data['message']['t'])
                    if 'p' in data['message']:
                        params['presValue'] = float(data['message']['p'])
                    if 'b' in data['message']:
                        params['batValue'] = float(data['message']['b'])
                except ValueError:
                    logging.error('Incorrect value: %s' % data['message'])
                    return
                
            elif data['result'] == 'error':
                s_data = data['message'].split(',')
                pipe_data = s_data[0].split(' ')
                logging.error('%s received: %s' % (self.hostname, data['message']))

            if params:
                message = [params, tags]
                dump = '%s\n' % json.dumps(message)

                try:
                    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sock.connect((self.service.config.NODE_RED_HOST, self.service.config.NODE_RED_PORT))
                    sock.send(dump.encode())
                except Exception as e:
                    logging.error('Node-red is offline')

                rh = helpers.RadioHelper(self.db_session)
                radio = rh.getByPipe(data['radio_pipe'])
                
                if radio:
                    so.emit('updateRadio', {'radio_id': radio.id, 'params': params}, broadcast=True)
                    
        elif 'type' in data and data['type'] == 'ir':
            logging.debug(data['ir_signal'])
            so.emit('recievedIr', {'result': 'success', 'ir_signal': data['ir_signal']}, broadcast=True)

    def parseMessage(data):
        message = {}

        return message
