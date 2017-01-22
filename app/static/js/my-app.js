// Initialize app
var myApp = new Framework7({
    //Tell Framework7 to compile templates on app init
    template7Pages: true,
    material: true,
    // domCache: false,
    // cache: false
});
 
// If we need to use custom DOM library, let's save it to $$ variable:
var $$ = Dom7;
 
// Add view
var mainView = myApp.addView('.view-main', {
  // Because we want to use dynamic navbar, we need to enable it for this view:
  // dynamicNavbar: true
});

$$.ajax({
	url: '/api/v1.0/devices',
	type: 'GET',
	success: function (data) {
		var d_obj = JSON.parse(data);
		if (d_obj.status_code != 100) {
			myApp.addNotification({
				message: 'Programm error',
				hold: 3000
			});
		}

		var devices = d_obj.devices ? d_obj.devices : [];

		mainView.router.load({
			url: 'static/devices.html',
			reload: true,
			context: {
				title: 'Choice device',
				devices: devices
			}
		});
		
		getTemperature();
	}
	// statusCode: {
	// 	401: function (xhr) {
	// 		myApp.loginScreen();
	// 	}
	// }
});

function getTemperature() {
	var tid = setInterval(setTimer, 2000);
	
	function setTimer() {
		$$.ajax({
			url: '/api/v1.0/device/therm/status',
			type: 'GET',
			success: function (data) {
				var d_obj = JSON.parse(data);
				if (d_obj.status_code != 100) {
					myApp.addNotification({
						message: 'Could not get temperature',
						hold: 3000
					});
					clearInterval(tid);
					return;
				}

				console.log(d_obj.result)

				// $$('div[data-page=devices] .temp').text("10");
			}
			// statusCode: {
			// 	401: function (xhr) {
			// 		myApp.loginScreen();
			// 	}
			// }
		});
	}
	// function abortTimer(tid) { // to be called when you want to stop the timer
	//   clearInterval(tid);
	// }
}

$$(document).on('pageInit', function (e) {
	console.log("aaaa");
	$$('.button-control').on('click', function() {
		var name = $$(this).closest('.page').attr('data-page');
		var command = $$(this).attr('data-command');

		$$.ajax({
			url: '/api/v1.0/device/' + name + '/' + command,
			type: 'GET',
			success: function (data) {
				var d_obj = JSON.parse(data);
				if (d_obj.status_code != 100) {
					myApp.addNotification({
						message: 'Programm error',
						hold: 3000
					});
				}
			}
			// statusCode: {
			// 	401: function (xhr) {
			// 		myApp.loginScreen();
			// 	}
			// }
		});
	});
});

/*
$$.ajax({
	url: ajax_host + '/admin/api/check_login',
	type: 'POST',
	success: function (data) {
		var d_obj = JSON.parse(data);
		if (d_obj.status_code == 100) {
			$$('#username').text(d_obj.result.current_user);
			current_bidder = d_obj.result.current_bidder;

			mainView.router.load({
				url: 'bid.html'
				// reload: true,
				// context: {
				// 	title: 'Bid'
				// }
			});
		}
	},
	statusCode: {
		401: function (xhr) {
			myApp.loginScreen();
		}
	}
});

$$('#bidding').on('click', function() {
	myApp.showIndicator();

	$$.ajax({
		url: ajax_host + '/admin/api/bidding',
		type: 'GET',
		statusCode: {
			401: function (xhr) {
				myApp.hideIndicator();
				myApp.loginScreen();
			}
		},
		success: function (data) {
			var d_obj = JSON.parse(data);
			if (d_obj.status_code == 100) {
				var auctions = d_obj.result === null ? [] : d_obj.result.auctions;

				mainView.router.load({
					url: 'bidding.html',
					reload: true,
					context: {
						title: 'Bidding',
						auctions: auctions,
						current_bidder: current_bidder
					}
				});
				$$('#bidding_count').text(auctions.length);
			} else {
				console.log(d_obj.message);
			}
			myApp.hideIndicator();
		}
	});
});

$$('#login').on('click', function() {
	var email = $$('input[name=username]').val();
	var password = $$('input[name=password]').val();

	if (!email || !password) {
		myApp.alert('Enter both username and password', 'Input error');
		return;
	}

	$$.ajax({
		url: ajax_host + '/admin/api/login',
		type: 'POST',
		data: {
			email: email,
			password: password
		},
		success: function (data) {
			var d_obj = JSON.parse(data);
			switch (d_obj.status_code) {
				case 10: 
					$$('#username').text(d_obj.result.current_user);
					current_bidder = d_obj.result.current_bidder;
					mainView.router.load({
						url: 'bid.html'
					});
					myApp.closeModal('.login-screen');
					break;
				case 20: 
					myApp.closeModal('.login-screen');
					break;
				case 30:
					myApp.alert('Login or password incorect', 'Login error');
					break;
			}
		}
	});
});

$$('#logout').on('click', function() {
	myApp.closePanel();
	$$.ajax({
		url: ajax_host + '/admin/api/logout',
		type: 'POST',
		success: function (data) {
			var d_obj = JSON.parse(data);
			console.log(d_obj);
			if (d_obj.status_code == 40) {
				myApp.loginScreen();
			}
		}
	});
});

myApp.onPageInit('bid', function (page) {
	$$('#bid').on('click', function() {

		var auc_id = $$('input[name=auc_id]').val();
		var price = $$('input[name=price]').val();

		if (!auc_id || !price) {
			myApp.alert('Enter both Lot ID and Price', 'Input error');
			return;
		}

		myApp.showIndicator();

		bid(auc_id, price, false);
	});
});

myApp.onPageInit('bidding', function (page) {
	$$('.bid-up').on('click', function() {

		var auc_id = $$(this).attr('data-id');

		myApp.prompt('Lot ID: ' + auc_id, 'Set new price', function (value) {
			var price = parseInt(value);
			if (!price) {
				return;
			}
			
			myApp.showIndicator();

			bid(auc_id, price, true);
		});
	});
});

function bid(auc_id, price, rebid) {
	$$.ajax({
		url: ajax_host + '/admin/api/bid',
		type: 'POST',
		data: {
			auc_id: auc_id,
			price: price
		},
		statusCode: {
			401: function (xhr) {
				myApp.hideIndicator();
				myApp.loginScreen();
			}
		},
		success: function (data) {
			var d_obj = JSON.parse(data);
			if (d_obj.status_code == 100) {

				if (rebid) {
					var card = $$('a[data-id=' + auc_id + ']').closest('.card');
					card.removeClass('card-red').addClass('card-green');
				}

				myApp.addNotification({
					message: d_obj.result,
					hold: 3000,
					additionalClass: 'bid-success'
				});
			} else {
				myApp.addNotification({
					message: d_obj.error,
					hold: 3000,
					additionalClass: 'bid-error'
				});
			}
			myApp.hideIndicator();
		}
	});
}
*/