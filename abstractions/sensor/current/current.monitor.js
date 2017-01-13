// ...

WebIOPi.prototype.newDevice = function(type, name) {

// ...

	if (type == "Current") {
		return new Current(name);
	}

// ...
	
}

// ...

// ----- Current -----

function Current(name) {
	this.name = name;
	this.url = "/devices/" + name + "/sensor";
	this.refreshTime = 1000;
}

Current.prototype.toString = function() {
	return this.name + ": Current";
}


Current.prototype.getMilliampere = function(callback) {
	$.get(this.url + "/current/mA", function(data) {
		callback(this.name, data);
	});
}

Current.prototype.refreshUI = function() {
	var temp = this;
	var element = this.element;
	if ((element != undefined) && (element.header == undefined)) {
		element.header = $("<h3>" + this + "</h3>");
		element.append(element.header);
	}
	
	this.getMilliampere(function(name, data){
		if (element != undefined) {
			element.header.text(temp + ": " + data + " mA");
		}
		setTimeout(function(){temp.refreshUI()}, temp.refreshTime);
	});
}
