// ...

WebIOPi.prototype.newDevice = function(type, name) {

// ...

	if (type == "Color") {
		return new Color(name);
	}

// ...
	
}

// ...

// ----- Color -----

function Color(name) {
	this.name = name;
	this.url = "/devices/" + name + "/sensor";
	this.refreshTime = 1000;
}

Color.prototype.toString = function() {
	return this.name + ": Color";
}

Color.prototype.getColorHex = function(callback) {
	var name = this.name
	$.get(this.url + "/color/rgb/hex", function(data) {
		callback(name, data);
	});
}

Color.prototype.refreshUI = function() {
	var color = this;
	var element = color.element;
	if ((element != undefined) && (element.header == undefined)) {
		element.header = $("<h3>" + color + "</h3>");
		element.append(element.header);
	}

	if ((element != undefined) && (element.table == undefined)) {
		element.table = $("<table>");
		element.append(element.table);

		var line= $("<tr>");

		var valueCell = $("<td>");
		valueCell.width(100);
		valueCell.attr("align", "left");
		var span = $("<span>");
		span.attr("id", "value_" + color.name);
		valueCell.append(span);
		line.append(valueCell);

		var colorCell = $("<td>");
		var span = $("<span>");
		span.text("--------------------------------------------------");
		colorCell.attr("id", "color_" + color.name);
		colorCell.append(span);
		line.append(colorCell);

		element.table.append(line);
	}

	this.getColorHex(function(name, data){
		$("#value_" + name).text(data);
		$("#color_" + name).attr("style", "background-color:" + data + "; color:" + data);
		setTimeout(function(){color.refreshUI()}, color.refreshTime);
	});
}
