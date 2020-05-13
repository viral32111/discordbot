// Choose a random item from an array
Array.prototype.random = function() {
	return this[ Math.floor( ( Math.random() * this.length ) ) ]
}