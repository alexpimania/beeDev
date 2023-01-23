function checkPassword(response)
{
    HTMLLoginDiv = document.getElementById("loginDiv");
    HTMLPassword = document.getElementById("password");
    HTMLStatus = document.getElementById("status");
    if (response === "Invalid Password")
    {
        HTMLPassword.value = "";
        HTMLLoginDiv.style.display = "block";
        HTMLStatus.innerHTML = "<span style='color: red'>Invalid Access Code</span>";
        return 1;
    }
    else
    {
        HTMLLoginDiv.style.display = "none";
        HTMLStatus.innerHTML = "<span style='color: green'>Valid Access Code</span>";
        return 0;
    }
}

function engineStart()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLStatsList = document.getElementById("statsList");
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            HTMLStatsList.innerHTML = req.responseText;
            resizeTextarea(HTMLStatsList);
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=statstEngine&action=statstart&password=" + HTMLpassword.value);
}

function engineStop()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLStatsList = document.getElementById("statsList");
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            HTMLStatsList.innerHTML = req.responseText;
            resizeTextarea(HTMLStatsList);
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=statstEngine&action=statstop&password=" + HTMLpassword.value);
}

function engineCheck()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLStatsList = document.getElementById("statsList");
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            HTMLStatsList.innerHTML = req.responseText;
            resizeTextarea(HTMLStatsList);
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=statstEngine&action=statcheck&password=" + HTMLpassword.value);
}

function getProfileNameList()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLProfileNameList = document.getElementById("profileNameList");
    HTMLProfileNameList.options.length = 0;
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            var APIResponseJSON = req.responseText;
            var profileNameList = JSON.parse(APIResponseJSON).sort();
            for (var profileIndex = 0; profileIndex < profileNameList.length; profileIndex++)
            {
                currentOption = document.createElement("option");
                currentOption.text = profileNameList[profileIndex];
                currentOption.value = profileNameList[profileIndex];
                HTMLProfileNameList.add(currentOption);
            }

            var profileNameListSize = HTMLProfileNameList.options.length / 2;
            if (profileNameListSize < 12)
            {
                HTMLProfileNameList.size = profileNameListSize;
            }
            else
            {
                HTMLProfileNameList.size = 12;
            }
        }

    };
    req.open("POST", "/beeServices/", true);
    req.send("function=getProfileNameList&password=" + HTMLpassword.value);
}

function getExchangeList()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLExchangeNameList = document.getElementById("exchangeList");
    HTMLExchangeNameList.options.length = 0;
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            var APIResponseJSON = req.responseText;
            var exchangeNameList = JSON.parse(APIResponseJSON).sort();
            for (var exchangeIndex = 0; exchangeIndex < exchangeNameList.length; exchangeIndex++)
            {
                currentOption = document.createElement("option");
                currentOption.text = exchangeNameList[exchangeIndex];
                currentOption.value = exchangeNameList[exchangeIndex];
                HTMLExchangeNameList.add(currentOption);
            }

            var exchangeNameListSize = HTMLExchangeNameList.options.length / 2;
            if (exchangeNameListSize < 12)
            {
                HTMLExchangeNameList.size = exchangeNameListSize;
            }
            else
            {
                HTMLExchangeNameList.size = 12;
            }
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=getExchangeList&password=" + HTMLpassword.value);
}

function updateProfile()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLExchangeNameList = document.getElementById("exchangeList");
    var HTMLProfileNameList = document.getElementById("profileNameList");
    var HTMLDepthText = document.getElementById("depthText");
    var HTMLFrequencyMins = document.getElementById("frequencyMins");
    var HTMLLastRunTime = document.getElementById("lastRunTime");
    var HTMLActive = document.getElementById("active");
    var HTMLProfileName = document.getElementById("profileName");

    var returnProfile = {};
    returnProfile.exchangeList = [];
    returnProfile.depthList = [];

    // Contruct object to return to API from screen values
    returnProfile.depthList = HTMLDepthText.value.split(' ').join('').split(",");
    returnProfile.frequencyMins = HTMLFrequencyMins.value;
    returnProfile.lastRunTime = HTMLLastRunTime.value;
    returnProfile.active = HTMLActive.checked;
    returnProfile.profileName = HTMLProfileName.value;

    // Save all of the highlighted excahanges to the object to return to the API
    for (var excahangeIndex = 0; excahangeIndex < HTMLExchangeNameList.options.length; excahangeIndex++)
    {
        if (HTMLExchangeNameList.options[excahangeIndex].selected)
        {
            returnProfile.exchangeList.push(HTMLExchangeNameList.options[excahangeIndex].value);
        }
    }
    // Convert the (now populated) profile object to JSON and send it to the backend API. i.e. save it.
    var returnProfileJSON = JSON.stringify(returnProfile);
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            // if new profile, add to profileNameList
            var inListBool = false;
            for (var profileIndex = 0; profileIndex < HTMLProfileNameList.options.length; profileIndex++)
            {
                if (HTMLProfileNameList.options[profileIndex].value == HTMLProfileName.value)
                {
                    inListBool = true;
                }
            }
            // Now display it in the profileList
            if (inListBool == false)
            {
                var newOption = document.createElement("option");
                newOption.text = HTMLProfileName.value;
                newOption.value = HTMLProfileName.value;
                HTMLProfileNameList.add(newOption);
            }
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=updateProfile&profileDetails=" + returnProfileJSON + "&password=" + HTMLpassword.value);
}

function getExchangeDetails()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLExchangeNameList = document.getElementById("exchangeList");
    var HTMLExchangeOrderbookButton = document.getElementById("showExchangeOrderbookButton");
    var HTMLexchangeOrderbookLink = document.getElementById("exchangeURL");
    if (HTMLExchangeNameList.selectedIndex != -1)
    {
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
            {
                var APIResponseJSON = req.responseText;
                var exchangeDetails = JSON.parse(APIResponseJSON);
                HTMLexchangeOrderbookLink.href = exchangeDetails.exchangeURL;
                HTMLExchangeOrderbookButton.title = "Show the selected exchange's orderbook";
            }
        };
        req.open("POST", "/beeServices/", true);
        req.send("function=getExchangeDetails&exchangeName=" + HTMLExchangeNameList.options[HTMLExchangeNameList.selectedIndex].value + "&password=" + HTMLpassword.value);
    }
    else
    {
        HTMLexchangeOrderbookLink.href = "void(0)";
        HTMLExchangeOrderbookButton.title = "Please select one exchange";
    }
}

function getProfileDetails()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLStatsList = document.getElementById("statsList");
    var HTMLProfileNameList = document.getElementById("profileNameList");
    var HTMLExchangeNameList = document.getElementById("exchangeList");
    var HTMLoutPutFileLink = document.getElementById("fileLink");
    var HTMLdepthField = document.getElementById("depthText");
    var HTMLProfileName = document.getElementById("profileName");
    var HTMLFrequencyMins = document.getElementById("frequencyMins");
    var HTMLActive = document.getElementById("active");
    var HTMLFileName = document.getElementById("fileName");
    var HTMLLastRunTime = document.getElementById("lastRunTime");

    HTMLStatsList.innerHTML = "";
    resizeTextarea(HTMLStatsList);

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            var APIResponseJSON = req.responseText;
            var profileDetails = JSON.parse(APIResponseJSON);
            HTMLProfileName.value = profileDetails.profileName;
            HTMLFrequencyMins.value = profileDetails.frequencyMins;
            HTMLActive.checked = (profileDetails.active == true);
            HTMLFileName.value = "bee_" + profileDetails.profileName + ".txt";
            HTMLLastRunTime.value = profileDetails.lastRunTime;

            // Highlight the exchanges for this profile (i.e. 'select' the exchange items in the select list)
            for (var exchangeIndex = 0; exchangeIndex < HTMLExchangeNameList.options.length; exchangeIndex++)
            {
                if (profileDetails.exchangeList.indexOf(HTMLExchangeNameList.options[exchangeIndex].value) in profileDetails.exchangeList)
                {
                    HTMLExchangeNameList.options[exchangeIndex].selected = true;
                }
                else
                {
                    HTMLExchangeNameList.options[exchangeIndex].selected = false;
                }
            }
            // Display the list of depths - as a CSV list (to make our life easy for the time being)
            var depthList = profileDetails.depthList;
            depthCSV = depthList.join(", ");
            HTMLdepthField.value = depthCSV;
            HTMLoutPutFileLink.href = "/beeServices/?function=getProfileTextFile&profileName=" + HTMLProfileName.value + "&password=" + HTMLpassword.value;
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=getProfileDetails&profileName=" + HTMLProfileNameList.options[HTMLProfileNameList.selectedIndex].value + "&password=" + HTMLpassword.value);
}

function clearScreen()
{
    document.getElementById("profileNameList").options.length = 0;
    document.getElementById("exchangeList").options.length = 0;
    document.getElementById("profileName").value = '';
    document.getElementById("frequencyMins").value = '';
    document.getElementById("active").checked = false;
    document.getElementById("fileName").value = '';
    document.getElementById("depthText").value = '';
    document.getElementById("lastRunTime").value = '';
    document.getElementById("statsList").innerHTML = "";
    resizeTextarea(document.getElementById("depthText"));
    setupPage();
}

function deleteProfile()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLProfileName = document.getElementById("profileName");
    selectedProfileName = HTMLProfileName.value;
    confirmDeleteBool = confirm('Any log file for this profile will also be deleted. Are you sure you want to delete the profile "' + selectedProfileName + '" ?');
    if (confirmDeleteBool == true)
    {
        var req = new XMLHttpRequest();
        req.onreadystatechange = function() {
            if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
            {
                clearScreen();
            }
        };
        req.open("POST", "/beeServices/", true);
        req.send("function=deleteProfile&profileName=" + selectedProfileName + "&password=" + HTMLpassword.value);

    }
}

function getProfileStatsCSV()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLProfileName = document.getElementById("profileName");
    var HTMLStatsList = document.getElementById("statsList");
    var selectedProfileName = HTMLProfileName.value; // then get the value. i.e. the currently-selected profileName.
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            var statsListASCI = req.responseText;
            HTMLStatsList.innerHTML = statsListASCI;
            resizeTextarea(HTMLStatsList);
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=getProfileStatsText&profileName=" + selectedProfileName + "&password=" + HTMLpassword.value);
}

function getProfileStatsJSON()
{
    var HTMLpassword = document.getElementById("password");
    var HTMLProfileName = document.getElementById("profileName");
    var HTMLStatsList = document.getElementById("statsList");
    var selectedProfileName = HTMLProfileName.value; // then get the value. i.e. the currently-selected profileName.
    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            var statsListJSON = req.responseText;
            HTMLStatsList.innerHTML = statsListJSON;
            resizeTextarea(HTMLStatsList);
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=getProfileStats&profileName=" + selectedProfileName + "&password=" + HTMLpassword.value);
}

function resizeTextarea(HTMLElement)
{
    HTMLElement.style.height = '24px';
    HTMLElement.style.height = HTMLElement.scrollHeight + 12 + 'px';
}

function setupPage()
{
    HTMLPassword = document.getElementById("password");
    HTMLLoginDev = document.getElementById("loginDiv");

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState == 4 && req.status == 200 && checkPassword(req.responseText) == 0)
        {
            HTMLLoginDev.style.display = "none";
            getProfileNameList();
            getExchangeList();
        }
    };
    req.open("POST", "/beeServices/", true);
    req.send("function=getExchangeList&password=" + HTMLPassword.value);
}

function getAveragePrice()
{
  var HTMLExchangeNameList = document.getElementById("exchangeList");
  var HTMLAveragePrice = document.getElementById("averageBitcoinPrice");
  var HTMLPassword = document.getElementById("password");
  var HTMLPriceDiv = document.getElementById("priceDiv");
  var selectedExchangeList = [];
  var fullExchangeList = [];
  var sumPrice = 0;
  var priceCount = 0;
  var exchangeIndex = 0;
  var HTMLRefreshIcon = document.getElementById("refreshIcon");
  
  
  function exchangePriceHandler()
  {
    if (this.readyState == 4 && this.status == 200 && checkPassword(this.responseText) == 0)
    {
      if (parseInt(this.responseText) != 0)
      {
          priceCount++;
          sumPrice = sumPrice + parseInt(this.responseText);
          HTMLAveragePrice.innerHTML = "USD $" + parseInt(sumPrice / priceCount).toFixed(2);
      }
      if (exchangeIndex + 1 <= selectedExchangeList.length && HTMLPriceDiv.style.display != "none")
      {
        exchangeIndex++;
        var req = new XMLHttpRequest(); 
        req.onreadystatechange = exchangePriceHandler;
        req.open("POST", "/beeServices/", true);
        req.send("function=getAveragePrice&exchanges=" + JSON.stringify([selectedExchangeList[exchangeIndex]]) + "&password=" + HTMLPassword.value);
      }
      else
      {
        HTMLRefreshIcon.src = "/refreshIcon.png";
      }
    }
  }
  
    for (var currentExcahangeIndex = 0; currentExcahangeIndex < HTMLExchangeNameList.options.length; currentExcahangeIndex++)
    {
      fullExchangeList.push(HTMLExchangeNameList.options[currentExcahangeIndex].value);
      if (HTMLExchangeNameList.options[currentExcahangeIndex].selected)
      {
          selectedExchangeList.push(HTMLExchangeNameList.options[currentExcahangeIndex].value);
      }
    }
    
    if (selectedExchangeList.length == 0)
    {
        selectedExchangeList = fullExchangeList;
    }
    
    var req = new XMLHttpRequest(); 
    req.onreadystatechange = exchangePriceHandler;
    req.open("POST", "/beeServices/", true);
    req.send("function=getAveragePrice&exchanges=" + JSON.stringify([selectedExchangeList[exchangeIndex]]) + "&password=" + HTMLPassword.value);
    HTMLRefreshIcon.src = "/refreshIconMoving.gif";
}
function togglePriceDiv()
{
  var HTMLPriceDiv = document.getElementById("priceDiv");
  if (HTMLPriceDiv.style.display == "block")
  {
    HTMLPriceDiv.style.display = "none";
  }
  else
  {
    HTMLPriceDiv.style.display = "block";
    getAveragePrice();
  }
}
