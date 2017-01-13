// ...

WebIOPi.prototype.newDevice = function(type, name) {

// ...

	if (type == "Power") {
		return new Power(name);
	}

// ...
	
}

// ...

// ----- Power -----

function Power(name) {
	this.name = name;
	this.url = "/devices/" + name + "/sensor";
	this.refreshTime = 1000;
}

Power.prototype.toString = function() {
	return this.name + ": Power";
}


Power.prototype.getWatt = function(callback) {
	$.get(this.url + "/power/W", function(data) {
		callback(this.name, data);
	});
}

Power.prototype.refreshUI = function() {
	var temp = this;
	var element = this.element;
	if ((element != undefined) && (element.header == undefined)) {
		element.header = $("<h3>" + this + "</h3>");
		element.append(element.header);
	}
	
	this.getWatt(function(name, data){
		if (element != undefined) {
			element.header.text(temp + ": " + data + " W");
		}
		setTimeout(function(){temp.refreshUI()}, temp.refreshTime);
	});
}
