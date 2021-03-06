
function startBedlam(consoleElement) {
	
	// The CoCo emulator
	var CoCoText = makeCoCoText(consoleElement);
	// The game code
	var BinaryData = makeBinaryDataBedlam();
	
    function write(addr,value) {        
    	if(addr>=0x0600 && addr<0x3F10) {
    		// RAM where the game is loaded
        	BinaryData.write(addr,value);
        	return true;
        }    	
    }
    
    function read(addr) { 
    	
        if(addr===0x0B6C) {            
        	// The real code calls the random number generator in the input loop.
        	// We are hijacking the input loop to let the wait happen in the
        	// browser. We patched the code (see BinaryDataBedlam.js) to include
        	// an extra routine to spin the RNG a number of times. We randomize
        	// that spin count here.
            write(0x3F05,Math.floor(Math.random()*8)+1);
            // Fall through
        }        
        
        if(addr===0x0A17) {
            // This is the long delay loop for flashing an error hint.
            // We want that wait to happen by the browser ... not in a 
            // spin within the code.
            CoCoText.pause();
            setTimeout(function() {
                CoCoText.runUntilWaitKey();
            },100);
            return 0x12; // NOP
        }
        if(addr===0x0A18) {
            // We hijacked the long-delay loop starting at 09D6. We returned
            // a NOP. When the CPU resumes it comes here. We already delayed,
            // so cancel the spin routine.
            return 0x39; // RTS
        }
                
        if(addr===0x117B) {
            // This is the game's endless-loop after death and such
            CoCoText.startEndlessLoop();            
        }
        
        if(addr>=0x0600 && addr<0x3F10) {
            // RAM where the game is loaded
            return BinaryData.read(addr); 
        }        
        
        return undefined;
        
    }
      
    BinaryData.loadDataCacheFromURL("/CoCo/Bedlam/Code.html",function() { 
    	CoCoText.init(read,write,function() {CoCoText.runUntilWaitKey();}, 0x0600);
    	CoCoText.runUntilWaitKey();    	  
    });    
    
};