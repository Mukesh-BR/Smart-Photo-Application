document.getElementById("displaytext").style.display = "none";
$('#label-input').tagsinput({
  tagClass: 'label label-default'
});

function resetData(){
    document.getElementById("displaytext").style.display = "none";
    document.getElementById("search-form").reset();
    document.getElementById("upload-form").reset();
    $('#label-input').tagsinput('removeAll');
    const imgs = document.getElementById("img-container");
    while (imgs.firstChild) {
        imgs.removeChild(imgs.lastChild);
    }
}

function searchPhoto(){

  var apigClient = apigClientFactory.newClient({
      apiKey: "PSMW3jzkfL9bheYtuXnbJyLC7FzhMyd9v9k1p6j3"
  });

    var query = document.getElementById('search-input').value;
    console.log("Query: " + query)
    if (!query){
        document.getElementById("modalMsg").innerHTML = "Query cannot be empty";
        $('#modalContainer').modal('show');
        return;
    }

    query = query.trim();
    var body = { };
    var params = {q : query};
    var additionalParams = {
        headers: {
            'Content-Type':"application/json"
        }
    };

    apigClient.searchGet(params, body , additionalParams).then(function(res){
        console.log(res)
        resetData();

        if(res.data.length == 0)
        {
          document.getElementById("displaytext").innerHTML = "No Images Found !!!"
          document.getElementById("displaytext").style.display = "block";
        }

        res.data.forEach( function(obj) {
            var img = new Image();
            img.src = obj["image-url"];
            img.setAttribute("class", "banner-img");
            img.setAttribute("alt", "effy");
            document.getElementById("displaytext").innerHTML = "Images returned for '"+query+"' are : "
            document.getElementById("img-container").appendChild(img);
            document.getElementById("displaytext").style.display = "block";
          });
        }).catch( function(result){
    });
}

function getBinary(file){
    return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      resolve(reader.result);
    };
    reader.onerror = error => reject(error);
    reader.readAsArrayBuffer(file);
  });
}

function uploadPhoto() {
   var file = document.getElementById('file-input').files[0];
   console.log(file);
   if (file == undefined){
       document.getElementById("modalMsg").innerHTML = "File not selected";
       $('#modalContainer').modal('show');
       return;
   }
   var labels = $("#label-input").val();
   console.log("Custom labels: " + labels);

   var image = getBinary(file).then(
     data => {
     console.log(data);
     var apigClient = apigClientFactory.newClient({
         apiKey: "KkM2FpGrGH1LhlvhijTaZ88GY0nQTk8faTu0KW2Q"
     });

     var body = data;
     var params = {'item' : file.name, 'Content-Type': file.type, 'x-amz-meta-customLabels': labels, 'folder' : 'myphotos1234'};
     var additionalParams = {};
     apigClient.uploadFolderItemPut(params, body , additionalParams).then(function(res){
       if (res.status == 200) {
           document.getElementById("modalMsg").innerHTML = "Image uploaded successfully!";
           $('#modalContainer').modal('show');
           resetData();
       }
     })
   });

}

function runSpeechRecognition() {
    // get output div reference
    var output = document.getElementById("search-input");
    // get action element reference
    var action = document.getElementById("action");
    // new speech recognition object
    try {
        var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        var recognition = new SpeechRecognition();
    }
    catch(e) {
        console.error(e);
        document.getElementById("modalMsg").innerHTML = "Speech recognition not supported!";
        $('#modalContainer').modal('show');
        $('.app').hide();
        return;
    }

    // This runs when the speech recognition service starts
    recognition.onstart = function() {
        action.innerHTML = "<small>listening, please speak...</small>";
    };

    recognition.onspeechend = function() {
        action.innerHTML = "<small>stopped listening, hope you are done...</small>";
        recognition.stop();
    }

    // This runs when the speech recognition service returns result
    recognition.onresult = function(event) {
        var transcript = event.results[0][0].transcript;
        var confidence = event.results[0][0].confidence;
        console.log("Transcript: " + transcript);
        console.log("Confidence: " + confidence);
        output.value = transcript;
    };

     // start recognition
     recognition.start();
}