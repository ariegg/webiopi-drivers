// ...

WebIOPi.prototype.newDevice = function(type, name) {

// ...

	if (type == "Memory") {
		return new Memory(name);
	}

// ...
	
}

// ...

// ----- Memory -----

function Memory(name) {
	this.name = name;
	this.url = "/devices/" + name + "/memory";
	this.refreshTime = 2000;
	this.byteCount = 0;
	
	var memory = this;
	$.get(this.url + "/byte/count", function(data) {
		memory.byteCount = parseInt(data);
	});
}

Memory.prototype.isReady = function() {
	return (this.byteCount > 0);
}

Memory.prototype.toString = function() {
	return this.name + ": Memory (" + this.byteCount + " bytes):";
}

Memory.prototype.memoryByteWildcard = function(callback) {
	var name = this.name
	$.get(this.url + "/byte/*", function(data) {
		callback(name, data);
	});
}

Memory.prototype.refreshUI = function() {
	var memory = this;
	var element = memory.element;
	if ((element != undefined) && (element.header == undefined)) {
		element.header = $("<h3>" + memory + "</h3>");
		element.append(element.header);
	}
	
	if ((element != undefined) && (element.table == undefined) && this.isReady()) {
		element.header.text(memory);
		element.table = $("<table>");
		element.append(element.table);

		var columns = memory.byteCount;
		var maxColumns = 16;
		if (columns > maxColumns) {
			columns = maxColumns;
		}

		var headerLine = $("<tr>");
		var cell = $("<th>");
		headerLine.append(cell);

		for (var i = 0; i<columns; i++) {
			var cell = $("<th>");
			cell.text(i.toString(16).toUpperCase());
			cell.attr("align", "right");
			headerLine.append(cell);
		}
		element.table.append(headerLine);

		for (var i = 0; i<(memory.byteCount / maxColumns) ; i++) {
			var dataLine= $("<tr>");
			var firstCell = $("<th>");
			firstCell.attr("align", "right");
                firstCell.attr("font", "monospace");
			firstCell.text("0x" + ("000" + (i*maxColumns).toString(16).toUpperCase()).substr(-4) + ":");

			dataLine.append(firstCell);
			for (var k = 0; k<maxColumns; k++) {
				var cell = $("<td>");
				cell.attr("align", "right");
				var span = $('<span>');
				span.attr("id", "span_" + memory.name + "_" + (i*maxColumns + k));
				cell.append(span);
				dataLine.append(cell);
			}
			element.table.append(dataLine);
		}
	}

	this.memoryByteWildcard(function(name, data) {
		for (i in data) {
			var span = $("#span_" + name + "_" + i);
			val = parseInt(data[i]).toString(16).toUpperCase();
			span.text(("0" + val).substr(-2));
		}
		setTimeout(function(){memory.refreshUI()}, memory.refreshTime);
	});
}
