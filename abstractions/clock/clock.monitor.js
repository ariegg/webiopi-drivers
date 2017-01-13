// ...

WebIOPi.prototype.newDevice = function(type, name) {

// ...

	if (type == "Clock") {
		return new Clock(name);
	}

// ...
	
}

// ...

// ----- Clock -----

function Clock(name) {
	this.name = name;
	this.url = "/devices/" + name + "/clock";
	this.refreshTime = 1000;
}

Clock.prototype.toString = function() {
	return this.name + ": Clock";
}

Clock.prototype.getDateTime = function(callback) {
	$.get(this.url + "/datetime", function(data) {
		callback(this.name, data);
	});
}

Clock.prototype.refreshUI = function() {
	var clock = this;
	var element = clock.element;
	if ((element != undefined) && (element.header == undefined)) {
		element.header = $("<h3>" + clock + "</h3>");
		element.append(element.header);
	}
	
	this.getDateTime(function(name, data){
		if (element != undefined) {
			element.header.text(clock + ": " + data);
		}
		setTimeout(function(){clock.refreshUI()}, clock.refreshTime);
	});
}
