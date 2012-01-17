/**
 * Copyright 2011, Joe Lambert (http://www.joelambert.co.uk)
 * Free to use under the MIT license.
 * http://www.opensource.org/licenses/mit-license.php
 */

var unshred = function(img, shredWidth) {
	var image = img,
		shredWidth = shredWidth || 32,
		pixelData = undefined,
		sortedData = [],
		unsortedData = [],
		i = s = 0,
		currentStripIndex = 0,
		
	pixel = function(r, g, b, a) {
		this.r = r;
		this.b = b;
		this.g = g;
		this.a = a;

		// Convert to YUV colourspace
		this.y = this.r *  .299000 + this.g *  .587000 + this.b *  .114000;
		this.u = this.r * -.168736 + this.g * -.331264 + this.b *  .500000 + 128;
		this.v = this.r *  .500000 + this.g * -.418688 + this.b * -.081312 + 128;

		// Work out the euclidean distance between two pixels based on the YUV colour space
		this.compare = function(pixel) {
			return Math.sqrt(
				((this.u - pixel.u) * (this.u - pixel.u)) +
				((this.v - pixel.v) * (this.v - pixel.v))
			);
		};
	},
	
	// (0, 0) Top left
	getPixelIndexXY = function(x, y) {
		return ((y * image.width) + x) * 4;
	},
	
	// Get a specific point in the pixel data
	getPixelDataXY = function(x, y) {
		var index = getPixelIndexXY(x, y);
		
		return new pixel(
			pixelData.data[index],		// r
			pixelData.data[index+1],	// g
			pixelData.data[index+2],	// b
			pixelData.data[index+3]		// a
		);
	},
	
	// Retrieve a strip of pixels from the image data
	getPixelStrip = function(x) {
		var data = [],
			i = 0;
		
		for(i=0; i<image.height; i++) {
			data.push(getPixelDataXY(x, i));
		}
		
		return data;
	},
	
	// Get a similarity score between pixel strips
	compareStrips = function(s1, s2) {
		var scores = [],
			totalCount = 0,
			i = 0;
		
		for(i=0; i< s1.length; i++) {
			var score = s1[i].compare(s2[i]);
			scores.push(score);
			totalCount += score;
		}
		
		return totalCount / s1.length;
	},
	
	// Create a canvas to load the image into to get the pixel data
	canvas = document.createElement("canvas"),
	ctx = canvas.getContext("2d"); 
	
	canvas.className  = "myClass";
	canvas.id = "myId";
	canvas.width = image.width;
	canvas.height = image.height;
	
	ctx.drawImage(image, 0, 0); 
	pixelData = ctx.getImageData(0, 0, image.width, image.height);
	
	// Iterate the image data
	for(i=0; i<image.width; i+=shredWidth) {
		var left = i,
			right = i+shredWidth-1,
		
		strip = {
			index: Math.ceil(i / shredWidth),
			left: getPixelStrip(left),
			right: getPixelStrip(right),
			coords: {
				x: left,
				y: 0,
				width: shredWidth,
				height: image.height
			},
			pixelData: ctx.getImageData(left, 0, shredWidth, image.height)
		};
		
		unsortedData.push(strip);
	}
	
	// Add the first strip to give us something to compare against
	sortedData.push(unsortedData[0]);
	unsortedData[0].used = true;
	
	// Iterate the rest of the 
	for(i=1; i<unsortedData.length; i++) {
		var leftIndex = rightIndex = leftScore = rightScore = undefined,
		
		// Get the left most strip that we know is sorted
		strip0 = sortedData[0],
		
		// Get the right most strip that we know is sorted
		strip1 = sortedData[sortedData.length-1];
		
		// Iterate all the unsorted data strips to find the best candidate for appending
		for(s=1; s<unsortedData.length; s++) {
			var strip2 = unsortedData[s], 
				lScore = rScore = undefined;
			
			if(strip2.used)
				continue;
			
			// Get a similarity score for placing this strip to the left of the current image
			lScore = compareStrips(strip0.left, strip2.right);
			
			// Get a similarity score for placing this strip to the right of the current image
			rScore = compareStrips(strip1.right, strip2.left);
			
			// If this score is better than the previous best, make this the best candidate for the left hand edge
			if(lScore < leftScore || leftScore === undefined) {
				leftScore = lScore;
				leftIndex = s;
			}

			// If this score is better than the previous best, make this the best candidate for the right hand edge
			if(rScore < rightScore || rightScore === undefined) {
				rightScore = rScore;
				rightIndex = s;
			}
		}
			
		if(rightScore < leftScore) {
			sortedData.splice(sortedData.length, 0, unsortedData[rightIndex]);
			unsortedData[rightIndex].used = true;
		}
		else {
			sortedData.splice(0, 0, unsortedData[leftIndex]);
			unsortedData[leftIndex].used = true;
		}
		
		currentStripIndex++;
	}
	
	return sortedData;
};