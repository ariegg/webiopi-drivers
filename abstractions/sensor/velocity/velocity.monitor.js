// ...

WebIOPi.prototype.newDevice = function(type, name) {

// ...

	if (type == "LinearVelocity") {
		return new LinearVelocity(name);
	}

	if (type == "AngularVelocity") {
		return new AngularVelocity(name);
	}

	return undefined;
}

// ...

// ----- Velocity -----

function LinearVelocity(name) {
	this.name = name;
	this.url = "/devices/" + name + "/sensor";
	this.refreshTime = 1000;
}

LinearVelocity.prototype.toString = function() {
	return this.name + ": LinearVelocity";
}

LinearVelocity.prototype.getMeterPerSecondX = function(callback) {
	$.get(this.url + "/velocity/linear/x/m_s", function(datax) {
		callback(this.name, datax);
	});
}

LinearVelocity.prototype.getMeterPerSecondY = function(callback) {
	$.get(this.url + "/velocity/linear/y/m_s", function(datay) {
		callback(this.name, datay);
	});
}

LinearVelocity.prototype.getMeterPerSecondZ = function(callback) {
	$.get(this.url + "/velocity/linear/z/m_s", function(dataz) {
		callback(this.name, dataz);
	});
}

LinearVelocity.prototype.refreshUI = function() {
	var linVelo = this;
	var element = this.element;
	
	if ((element != undefined) && (element.header == undefined)) {
		element.header = $("<h3>" + this + "</h3>");
		element.append(element.header);
		var dimlist = $('<ul>');
		element.append(dimlist);
		element.liX = $('<li>');
		dimlist.append(element.liX);
		element.liY = $('<li>');
		dimlist.append(element.liY);
		element.liZ = $('<li>');
		dimlist.append(element.liZ);
	}
	
	this.getMeterPerSecondX(function(name, datax){
		if (element != undefined) {
			element.liX.text("X-axis -- (forth/back) --> " + datax + " m/s");
		}
		setTimeout(function(){linVelo.refreshUI()}, linVelo.refreshTime);
	});

	this.getMeterPerSecondY(function(name, datay){
		if (element != undefined) {
			element.liY.text("Y-axis -- (left/right) ----> " + datay + " m/s");
		}
	});

	this.getMeterPerSecondZ(function(name, dataz){
		if (element != undefined) {
			element.liZ.text("Z-axis -- (up/down) ----> " + dataz + " m/s");
		}
	});
}


function AngularVelocity(name) {
	this.name = name;
	this.url = "/devices/" + name + "/sensor";
	this.refreshTime = 1000;
}

AngularVelocity.prototype.toString = function() {
	return this.name + ": AngularVelocity";
}

AngularVelocity.prototype.getRadianPerSecondX = function(callback) {
	$.get(this.url + "/velocity/angular/x/rad_s", function(datax) {
		callback(this.name, datax);
	});
}

AngularVelocity.prototype.getRadianPerSecondY = function(callback) {
	$.get(this.url + "/velocity/angular/y/rad_s", function(datay) {
		callback(this.name, datay);
	});
}

AngularVelocity.prototype.getRadianPerSecondZ = function(callback) {
	$.get(this.url + "/velocity/angular/z/rad_s", function(dataz) {
		callback(this.name, dataz);
	});
}

AngularVelocity.prototype.refreshUI = function() {
	var angVelo = this;
	var element = this.element;
	
	if ((element != undefined) && (element.header == undefined)) {
		element.header = $("<h3>" + this + "</h3>");
		element.append(element.header);
		var dimlist = $('<ul>');
		element.append(dimlist);
		element.liX = $('<li>');
		dimlist.append(element.liX);
		element.liY = $('<li>');
		dimlist.append(element.liY);
		element.liZ = $('<li>');
		dimlist.append(element.liZ);
	}
	
	this.getRadianPerSecondX(function(name, datax){
		if (element != undefined) {
			element.liX.text("X-axis -- (roll) ----> " + datax + " rad/s");
		}
		setTimeout(function(){angVelo.refreshUI()}, angVelo.refreshTime);
	});

	this.getRadianPerSecondY(function(name, datay){
		if (element != undefined) {
			element.liY.text("Y-axis -- (pitch) --> " + datay + " rad/s");
		}
	});

	this.getRadianPerSecondZ(function(name, dataz){
		if (element != undefined) {
			element.liZ.text("Z-axis -- (yaw) ---> " + dataz + " rad/s");
		}
	});
}
