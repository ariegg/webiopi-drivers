// ...

WebIOPi.prototype.newDevice = function(type, name) {

// ...

	if (type == "Voltage") {
		return new Voltage(name);
	}

// ...
	
}

// ...

// ----- Voltage -----

function Voltage(name) {
	this.name = name;
	this.url = "/devices/" + name + "/sensor";
	this.refreshTime = 1000;
}

Voltage.prototype.toString = function() {
	return this.name + ": Voltage";
}


Voltage.prototype.getVolt = function(callback) {
	$.get(this.url + "/voltage/V", function(data) {
		callback(this.name, data);
	});
}

Voltage.prototype.refreshUI = function() {
	var temp = this;
	var element = this.element;
	if ((element != undefined) && (element.header == undefined)) {
		element.header = $("<h3>" + this + "</h3>");
		element.append(element.header);
	}
	
	this.getVolt(function(name, data){
		if (element != undefined) {
			element.header.text(temp + ": " + data + " V");
		}
		setTimeout(function(){temp.refreshUI()}, temp.refreshTime);
	});
}
