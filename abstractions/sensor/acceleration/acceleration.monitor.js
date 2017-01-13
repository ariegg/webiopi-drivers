// ...

WebIOPi.prototype.newDevice = function(type, name) {

// ...

	if (type == "LinearAcceleration") {
		return new LinearAcceleration(name);
	}

	if (type == "AngularAcceleration") {
		return new AngularAcceleration(name);
	}

	return undefined;
}

// ...

// ----- Acceleration -----

function LinearAcceleration(name) {
	this.name = name;
	this.url = "/devices/" + name + "/sensor";
	this.refreshTime = 1000;
}

LinearAcceleration.prototype.toString = function() {
	return this.name + ": LinearAcceleration";
}

LinearAcceleration.prototype.getMeterPerSquareSecondX = function(callback) {
	$.get(this.url + "/acceleration/linear/x/m_s2", function(datax) {
		callback(this.name, datax);
	});
}

LinearAcceleration.prototype.getMeterPerSquareSecondY = function(callback) {
	$.get(this.url + "/acceleration/linear/y/m_s2", function(datay) {
		callback(this.name, datay);
	});
}

LinearAcceleration.prototype.getMeterPerSquareSecondZ = function(callback) {
	$.get(this.url + "/acceleration/linear/z/m_s2", function(dataz) {
		callback(this.name, dataz);
	});
}

LinearAcceleration.prototype.getGravityX = function(callback) {
	$.get(this.url + "/acceleration/gravity/x/g", function(datax) {
		callback(this.name, datax);
	});
}

LinearAcceleration.prototype.getGravityY = function(callback) {
	$.get(this.url + "/acceleration/gravity/y/g", function(datay) {
		callback(this.name, datay);
	});
}

LinearAcceleration.prototype.getGravityZ = function(callback) {
	$.get(this.url + "/acceleration/gravity/z/g", function(dataz) {
		callback(this.name, dataz);
	});
}

LinearAcceleration.prototype.refreshUI = function() {
	var linAccel = this;
	var element = this.element;
	
	if ((element != undefined) && (element.header == undefined)) {

		element.header = $("<h3>" + this + "</h3>");
		element.append(element.header);
		var para = $('<p>');
		element.append(para);
		
		var checkbox = $('<input type="checkbox">');
		checkbox.attr("id", "checkbox_" + this.name + "_gravity");

		var cblabel = $('<label>');
		cblabel.append(checkbox);
		cblabel.append("Show gravity");
		para.append(cblabel);
		
		var dimlist = $('<ul>');
		element.append(dimlist);
		element.liX = $('<li>');
		dimlist.append(element.liX);
		element.liY = $('<li>');
		dimlist.append(element.liY);
		element.liZ = $('<li>');
		dimlist.append(element.liZ);
	}
	
	var checkbox = $("#checkbox_" + this.name + "_gravity");
	var gravity = checkbox.is(":checked")

	if (!gravity) {

		this.getMeterPerSquareSecondX(function(name, datax){
			if (element != undefined) {
				element.liX.text("X-axis -- (forth/back) --> " + datax + " m/s^2");
			}
			setTimeout(function(){linAccel.refreshUI()}, linAccel.refreshTime);
		});

		this.getMeterPerSquareSecondY(function(name, datay){
			if (element != undefined) {
				element.liY.text("Y-axis -- (left/right) ----> " + datay + " m/s^2");
			}
		});

		this.getMeterPerSquareSecondZ(function(name, dataz){
			if (element != undefined) {
				element.liZ.text("Z-axis -- (up/down) ----> " + dataz + " m/s^2");
			}
		});
	}

	else {

		this.getGravityX(function(name, datax){
			if (element != undefined) {
				element.liX.text("X-axis -- (forth/back) --> " + datax + " g");
			}
			setTimeout(function(){linAccel.refreshUI()}, linAccel.refreshTime);
		});

		this.getGravityY(function(name, datay){
			if (element != undefined) {
				element.liY.text("Y-axis -- (left/right) ----> " + datay + " g");
			}
		});

		this.getGravityZ(function(name, dataz){
			if (element != undefined) {
				element.liZ.text("Z-axis -- (up/down) ----> " + dataz + " g");
			}
		});
	}

}


function AngularAcceleration(name) {
	this.name = name;
	this.url = "/devices/" + name + "/sensor";
	this.refreshTime = 1000;
}

AngularAcceleration.prototype.toString = function() {
	return this.name + ": AngularAcceleration";
}

AngularAcceleration.prototype.getRadianPerSquareSecondX = function(callback) {
	$.get(this.url + "/acceleration/angular/x/rad_s2", function(datax) {
		callback(this.name, datax);
	});
}

AngularAcceleration.prototype.getRadianPerSquareSecondY = function(callback) {
	$.get(this.url + "/acceleration/angular/y/rad_s2", function(datay) {
		callback(this.name, datay);
	});
}

AngularAcceleration.prototype.getRadianPerSquareSecondZ = function(callback) {
	$.get(this.url + "/acceleration/angular/z/rad_s2", function(dataz) {
		callback(this.name, dataz);
	});
}

AngularAcceleration.prototype.refreshUI = function() {
	var angAccel = this;
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
	
	this.getRadianPerSquareSecondX(function(name, datax){
		if (element != undefined) {
			element.liX.text(" X-axis -- (roll) ----> " + datax + " rad/s^2");
		}
		setTimeout(function(){angAccel.refreshUI()}, angAccel.refreshTime);
	});

	this.getRadianPerSquareSecondY(function(name, datay){
		if (element != undefined) {
			element.liY.text("Y-axis -- (pitch) --> " + datay + " rad/s^2");
		}
	});

	this.getRadianPerSquareSecondZ(function(name, dataz){
		if (element != undefined) {
			element.liZ.text("Z-axis -- (yaw) ---> " + dataz + " rad/s^2");
		}
	});
}
