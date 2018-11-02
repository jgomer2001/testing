function err(data) {
	alert(data)
}
/*
function getTokenUrl(openidUrl, callback) {
	$.get(openidUrl)
			.fail(() => err())
			.done(result => result.token_endpoint).then(() => alert('result'))//callback()
}
*/
function genericGET(url) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open("GET", url)
    xhr.onload = () => resolve(xhr.responseText)
    xhr.onerror = () => reject(xhr.statusText)
    xhr.send()
  })
}

function genericPOST(url, headers, payload) {
	return new Promise((resolve, reject) => {
		var xhr = new XMLHttpRequest()
		xhr.open("POST", url)
		for (var i = 0; i < headers.length; i++) {
			xhr.setRequestHeader(headers[i].name, headers[i].value)
		}
		xhr.onload = () => resolve(xhr.responseText)
		xhr.onerror = () => reject(xhr.statusText)
		xhr.send(payload)
	})
}

function getTokenUrl(openidUrl) {
	return genericGET(openidUrl)
				.then(result => JSON.parse(result).token_endpoint)
}

function getToken(url, clientId, clientSecret) {

	var auth = "Basic " + window.btoa(clientId + ":" + clientSecret)
	var headers = [
			{name : "Authorization", value : auth},
			{name : "Content-Type", value : "application/x-www-form-urlencoded"}
	]
	var payload = "grant_type=client_credentials"
	return genericPOST(url, headers, payload)
				.then(result => JSON.parse(result).access_token)
}