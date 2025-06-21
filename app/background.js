// background.js - coordinates tasks between content.js and the API

(function() {

  var totalParagraphs = 0;

  /*
   * Listener to capture text that needs to be simplified
   * The request should look like:
   *    {from: "content",
   *    toSimplify: [...sentences to simplify]}
   */
  chrome.runtime.onMessage.addListener(async function (request) {
    if (request.from === "popup") {
        const gradeLevel = request.gradeLevel; // Get the grade level from popup

        // Define a mapping for grade levels to adjust the simplification prompt
        let gradePrompt = "";
        if (gradeLevel === "Elementary") {
            gradePrompt = "Reader has elementary level reading proficiency.";
        } else if (gradeLevel === "High-School") {
            gradePrompt = "Reader has high school level reading proficiency.";
        } else if (gradeLevel === "College") {
            gradePrompt = "Reader has college-level reading proficiency.";
        }

        sentenceData = request.toSimplify;
        await getNewText(sentenceData, "sentence", gradePrompt);
    }
});

 

  /**
   * Perform API call to simplify text
   * POST request body example : {"type": "sentence", "text": "apple" } - stringified
   * @param {*} text the full string that needs to be simplified
   * @param {*} type type of text being sent, we have only used at the sentence level
   *                 but views.py in the API can be modified to accept other levels
   * @returns a JSON object containing simplified versions of the provided text argument that
   * align with the simplification settings, currently pulled from sample.json
   */
  async function requestSimplification(text, type, gradePrompt) {

    // Modify the text to include the grade-level prompt
    let modifiedText = `${text} ${gradePrompt}`;

    // This URL points to the API server and the name of the directory within the API
    let url = "http://127.0.0.1:8000/simplify/";
    
    // Number of paragraphs
    let amount = type === "document" ? `${totalParagraphs}/` : "";
    let response = await fetch(url + amount, {
      mode: "cors",
      method: "POST",
      body: JSON.stringify({ type: type, text:  modifiedText }),
      headers: {
        "Content-Type": "application/json",
      },
      redirect: "follow",
    });


    if (!response.ok) {
      throw new Error(`HTTP error status: ${response.status}`);
    } else {
      freshTextPromise = await response.text();
      freshTextPromise = freshTextPromise.replace(/^"(.*)"$/, "$1");
      return freshTextPromise;
    }
  }

  /**
   * Helper function to go through the given data to call the API. After receiving the 
   * simplifications, this function sends a message that is parsed by content.js
   * with the simplified text.
   * @param {*} data a dictionary with the text to request simplifications for where
   *                 the keys are an ID for the text and the value the actual text
   * @param {*} type type of text being sent, we have only used at the sentence level
   *                 but views.py in the API can be modified to accept other levels
   */
  async function getNewText(data, type, gradePrompt) {
    var toSendBack = [];

    var keys = Object.keys(data);
    for (var i = 0; i < keys.length; i++) {
      textID = keys[i];

      // Add grade-level prompt to text before simplifying
      let simple = await requestSimplification(data[textID], type, gradePrompt);
      toSendBack.push({ sentenceID: textID, text: simple });
    }

    
    // send to content script and modify those words
    let toSend = JSON.stringify(toSendBack);

    if (toSendBack.length === keys.length) {
      chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {
          from: "API",
          toChange: toSend,
          textType: type,
        });
      });
    }
  }

})();

// Function to send ASL data to Dr. Alonzo’s live feedback system (pore add)
async function sendToLiveFeedbackSystem(data) {
  const feedbackUrl = "https://api.dralonzosystem.com/feedback";  // example URL
  let response = await fetch(feedbackUrl, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
  });

  if (!response.ok) {
      console.error("Error connecting to the live feedback system");
      return null;
  }
  return await response.json(); // Assume it returns feedback data
}
