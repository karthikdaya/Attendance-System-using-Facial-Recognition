function ShowCam() {
    Webcam.set({
        width: 320,
        height: 240 ,
        image_format: 'jpg',
        jpeg_quality: 100
    });
    Webcam.attach('#my_camera');
}
window.onload= ShowCam;

function snap() {
    Webcam.snap( function(data_uri) {
        // display results in page
        document.getElementById('results').innerHTML = '<img id="image" src="'+data_uri+'"/>';
      } );      
}


function upload() {
    console.log("Uploading...");
    var image = document.getElementById('image').src;
    console.log(image);
    var form = document.getElementById('myForm');
    var formData = new FormData(form);
    formData.append("file", image);
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/signup");
    // check when state changes, 
    xmlhttp.onreadystatechange = function() {
    	if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
    	//	alert(xmlhttp.responseText);
    	//check if signp was success, if yes then redirect or show message
    	document.getElementById("myForm").reset();
    	  alert("Record saved successfully");
    	          	window.location.assign("/signup");


    	}
    }
    xmlhttp.send(formData);
}

function upload1() {
    console.log("Uploading...");
    var image = document.getElementById('image').src;
    console.log(image);
    console.log("!!!!");
    var form = document.getElementById('myForm');
    var formData = new FormData(form);
    formData.append("file", image);
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/showcam");
    // check when state changes,
    xmlhttp.onreadystatechange = function() {
    	if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        	document.getElementById("myForm").reset();
    	    var msg = JSON.parse(xmlhttp.responseText);
    	    console.log(msg);
    	    alert(msg.reply)
        	window.location.assign("/showcam");
    	}
    }
    xmlhttp.send(formData);
}

function upload2() {
    console.log("Uploading...");
    var form = document.getElementById('myForm');
    var formData = new FormData(form);
     if(document.getElementById('camera').style.display=='block'){
            var image = document.getElementById('image').src;
    formData.append("file", image);
     }
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "/editstudent");
    // check when state changes,
    xmlhttp.onreadystatechange = function() {
    	if(xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        	document.getElementById("myForm").reset();
    	 alert("Details updated successfully");
        	window.location.assign("/login");
    	}
    }
    xmlhttp.send(formData);
}