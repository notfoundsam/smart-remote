import serial, socket, threading
import time, random, json, array
import os, sys, logging
from app import so, config, cache
from app.helpers import NodeHelper, RadioHelper, MqttHelper

class Service():

    def __init__(self):
        self.first_request = None
        self.node_listener = None
        self.mqtt_listener = None
        self.discover_service = None

    def activateDiscoverService(self):
        self.discover_service = DiscoverService()
        self.discover_service.start()
    
    def activateNodeListener(self):
        self.node_listener = NodeListener()
        self.node_listener.start()
    
    def activateMqttListener(self):
        self.mqtt_listener = MqttListener()
        self.mqtt_listener.start()

class DiscoverService(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logging.info('Starting the discover service')
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            message = "s-hostname:%s" % socket.gethostname()
            sock.sendto(message.encode(), (config.BROADCAST_MASK, config.BROADCAST_PORT))
            time.sleep(config.BROADCAST_INTERVAL)

class NodeListener(threading.Thread):

    def __init__(self):
        self.nodes = {}
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((config.NODE_LISTENER_BIND_ADDRESS, config.NODE_LISTENER_BIND_PORT))        
        sock.listen(config.NODE_LISTENER_CONNECTIONS)

        while True:
            conn, addr = sock.accept()
            node = RpiNode(self, conn, addr)
            node.start()

    def addNode(self, node):
        db_session = config.getNewDbSession()
        nh = NodeHelper(db_session)
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

class MqttListener(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((config.MQTT_LISTENER_BIND_ADDRESS, config.MQTT_LISTENER_BIND_PORT))        
        sock.listen(config.MQTT_LISTENER_CONNECTIONS)

        while True:
            conn, addr = sock.accept()
            logging.info('New connection from MQTT %s' % addr[0])
            
            message_buff = ''

            while True:
                try:
                    data = conn.recv(1)
                    if data:
                        udata = data.decode()

                        if udata != "\n":
                            message_buff += udata
                            continue

                        logging.debug(message_buff)
                        mp = MqttMessageParser(message_buff)
                        mp.run()
                        message_buff = ''
                    else:
                        logging.info('Connection closed for MQTT %s' % self.addr[0])
                        break
                except Exception as e:
                    logging.error('Socket error, close connection MQTT')
                    logging.error(e)
                    break

            conn.close()

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
        logging.info('New connection from Node %s' % self.addr[0])
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
                        np = NodeMessageParser(self.hostname, message_buff)
                        np.run()

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

class NodeMessageParser():

    def __init__(self, hostname, data):
        # threading.Thread.__init__(self)
        self.hostname = hostname
        self.data = data
        
    def run(self):
        try:
            data = json.loads(self.data)
        except ValueError as e:
            logging.debug(self.data)
            logging.error('Broken json from socket')
            return

        if 'type' in data and data['type'] == 'response':
            logging.debug('%s received: %s' % (self.hostname, self.data))

            if 'origin_event' in data and data['origin_event'] is not None and 'room' in data['origin_event']:
                if data['result'] == 'error':
                    # so.emit('notification', {'result': data['result'], 'error': data['error']}, broadcast=True)
                    so.emit('notification', {'result': data['result'], 'error': data['error']}, room=data['origin_event']['room'])
                else:
                    # so.emit('notification', {'result': data['result']}, broadcast=True)
                    so.emit('notification', {'result': data['result']}, room=data['origin_event']['room'])

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
                message = {'type': 'log', 'message': [params, tags]}
                dump = '%s' % json.dumps(message)

                try:
                    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sock.connect((config.NODE_RED_HOST, config.NODE_RED_PORT))
                    sock.send(dump.encode())
                except Exception as e:
                    logging.error('Node-red is offline')

                db_session = config.getNewDbSession()
                rh = RadioHelper(db_session)
                radio = rh.getByPipe(data['radio_pipe'])
                db_session.close()
                
                if radio:
                    logging.debug(radio.id)
                    logging.debug(params)
                    so.emit('updateRadio', {'radio_id': radio.id, 'params': params}, broadcast=True)
                    cache.setRadioParams(radio.id, params)
                    
        elif 'type' in data and data['type'] == 'ir':
            if 'origin_event' in data and data['origin_event'] is not None and 'room' in data['origin_event']:
                logging.debug('-- ir event --')
                if data['result'] == 'success':
                    so.emit('recievedIr', {'result': 'success', 'ir_signal': data['ir_signal']}, room=data['origin_event']['room'])
                elif data['result'] == 'error':
                    so.emit('recievedIr', {'result': 'error', 'error': data['error']}, room=data['origin_event']['room'])

    def parseMessage(data):
        message = {}

        return message

class MqttMessageParser():

    def __init__(self, data):
        self.data = data
        
    def run(self):
        try:
            data = json.loads(self.data)
        except ValueError as e:
            logging.debug(self.data)
            logging.error('Broken json from socket')
            return

        if 'tp' in data and data['tp'] == 'rs':
            pass

        elif 'tp' in data and data['tp'] == 'ev':
            params = {}
            tags = {}

            if 'cl' in data:
                tags['mqtt_client'] = data['cl']
            try:
                if 'h' in data:
                    params['humiValue'] = float(data['h'])
                if 't' in data:
                    params['tempValue'] = float(data['t'])
                if 'p' in data:
                    params['presValue'] = float(data['p'])
                if 'b' in data:
                    params['batValue'] = float(data['b'])
            except ValueError:
                logging.error('Incorrect value: %s' % data['message'])
                return

            if params:
                message = {'type': 'log', 'message': [params, tags]}
                dump = '%s' % json.dumps(message)

                try:
                    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sock.connect((config.NODE_RED_HOST, config.NODE_RED_PORT))
                    sock.send(dump.encode())
                except Exception as e:
                    logging.error('Node-red is offline')

                db_session = config.getNewDbSession()
                mh = MqttHelper(db_session)
                mqtt = mh.getByClientName(data['cl'])
                db_session.close()
                
                if mqtt:
                    logging.debug(params)
                    so.emit('updateMqtt', {'mqtt_id': mqtt.id, 'params': params}, broadcast=True)
                    cache.setMqttParams(mqtt.id, params)
