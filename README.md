# 
 

|Example|Details|
|-|-|
|<pre>obj = { salutation: "Hey!", ... }
result = RRF "survey.ftl" obj
</pre>|Renders the template `survey.ftl` (located in this flow's base path) and resulting markup is replied to user's browser.<br/>Data submitted by the user is ignored|
|`obj = { salutation: "Hey!", ... }`<br/>`result = RRF "survey.ftl" obj`|Renders the template `survey.ftl` by injecting the data passed in `obj` and the resulting markup is replied to user's browser.<br/>Data submitted by the user is stored in variable `result`: a map whose keys are named according to the form fields present in `survey.ftl`|

<table>
	<tr><th>Code</th><th>Meaning</th></tr>
	<tr>
		<th>
<pre>it = { success: true, data: { userId: "as9233Qz", ... }}
Finish it</pre>
		</th>
		<th>Flow finished successfully. Some relevant data attached</th>
	</tr>
	<tr>
		<th>
<pre>it = { success: false,
    error: "User entered a wrong password 3 times" }
Finish it</pre>
		</th>
		<th>Flow failed. Error description attached</th>
	</tr>
</table>