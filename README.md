# 
 

|Example|Details|
|-|-|
|`RRF "survey.ftl"`|Renders the template `survey.ftl` (located in this flow's base path) and resulting markup is replied to user's browser.<br/>Data submitted by the user is ignored|
|`obj = { salutation: "Hey!", ... }`<br/>`result = RRF "survey.ftl" obj`|Renders the template `survey.ftl` by injecting the data passed in `obj` and the resulting markup is replied to user's browser.<br/>Data submitted by the user is stored in variable `result`: a map whose keys are named according to the form fields present in `survey.ftl`|

