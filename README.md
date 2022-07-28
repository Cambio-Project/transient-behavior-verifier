### [Link to the thesis and the supplementary material](https://doi.org/10.5281/zenodo.6845089)

DOI: 10.5281/zenodo.6845089

# Outline

1. [Architecture](#Architecture)
2. [How to run the tool in a docker container](#How-to-run-the-tool-in-a-docker-container)
3. [How to run the correctness evaluation](#How-to-run-the-correctness-evaluation)
4. [How to extend the predicate functions](#How-to-extend-the-predicate-functions)
5. [REST API](##REST-API)
6. [JSON specification description](#json-specification-description)


## Architecture

The architecture of the tool consists of the following components:
![](https://i.imgur.com/HhlTJVs.png)

#### REST API
The REST API is implemented in the ```gui_endpoints.py``` and ```logic_endpoints.py``` files. The first one implements the the endpoints that serve the GUI of the tool while the second one implements the logical operations that are provided by the API. More about the endpoints can be found below.

#### GUI

The GUI of the tool consists of several HTML pages built by using Bootstrap and JavaScript. 

#### Parser

The parser component consists of the files in the ```src/handlers/``` folder. This component is responsible for the mapping of PSPs to MTL formula and for the parsing and preparing of the formulas and the predicates. 

#### Data Retriever

The Data Retriever contains one abstract class and three subclasses extending it. The abstract class defines the common behavior of the data retrieval. The three classes extending it are defining the retrieval for InfluxDB, Prometheus, and CSV files.

#### Evaluator

The evaluator is implemented in the ```src/mtl_evaluation/mtl_evaluator.py``` file. It receives an MTL formula, a prepared event trace, and some additional informations. The verification of the formula is started by calling the [python-monitors](https://github.com/doganulus/python-monitors) library. The results of the verfication are then passed to the plotter.

#### Plotter
The plotter is implemented in the ```src/mtl_evaluation/mtl_plotter.py``` file. It receives the results of the verification from the evaluator and creates the result plots. The plots are located in ```src/static/results.pdf``` and can be retrieved by accessing ```localhost:5000/static/results.pdf```

## How to run the tool in a docker container:

1. Navigate to the src folder
2. Build the docker image:

```
docker build . -t transient-behavior-verifier
```

3. Run the container:

```
docker run -p 5000:5000 transient-behavior-verifier
```

4. You should now be able to access the web UI via ```localhost:5000```

## How to run the correctness evaluation:

In order to run the correctness evaluation, copy the contents of the correctness evaluation folder into ```src/static```. Then import the postman collections into postman and make sure that the ```remote-csv-address``` fields point to the correct paths.  

## How to extend the predicate functions:

The predicate functions are located in the ```Predicates``` class located in ```src/handlers/predicate_functions.py```. Below are presented some example predicate functions contained in the class:
```
class Predicates:
    def __init__(self, value=None):
        self.value = value
        self.trendLast = None
    def equal(self, variable):
        return variable == self.value
    def notEqual(self, variable):
        return variable != self.value
    def bigger(self, variable):
        return variable > self.value
    def smaller(self, variable):
        return variable < self.value
```
In order to add new fuctions, simply define define additional functions that return a Boolean value. The method parameters such as ```variable``` are used to pass the measurement values into the predicate. The prototype also supports multiple variables in one predicate, i.e. ```f(x,y)```. 

## REST API

The prototype implements a REST API. All available endpoints are listed below together with information about them:


| URL | Method | Body | Info |
| -------- | -------- | -------- | -------- |
| ```/monitor```     | ```POST```   | A JSON object containg a transient behavior specification. | Initiates the evaluation of a transient behavior specificaiton.     |
| ```/insert_spec_into_exp```     | ```POST```  |  ```multipart/form-data``` - containing a transient behavior specification and a JSON file containig a chaos experiment.  | Inserts a transient behavior specification into a CTK chaos experiment and returns it as a downloadable file.     |
| ```/save_spec```     | ```POST```   | ```form-data``` containing a transient behavior specification. | Saves a transient behavior specification in a JSON file.     |
| ```/result```     | ```GET, POST```  |   | Runs a transient behavior verification by calling the ```/monitor``` endpoint and returns the page visualizing the results.     |
| ```/```     | ```GET```  |   | Returns the welcoming page.     |
| ```/index```     | ```GET```  |   | Also returns the welcoming page.     |
| ```/create_spec_mtl```     | ```GET```  |   | Returns the page for creating a transient behavior specification using an MTL formula.     |
| ```/create_spec_psp```     | ```GET```   |  | Returns the page for creating a transient behavior specification using a PSP definition.     |
| ```/spec_selector```     | ```GET```   |  | Returns the page in which the user can select the way to define the behavior specification, i.e. MTL or PSP.     |
| ```/create_exp```     | ```GET```   |  | Returns the page where a transient behavior specification can be inserted into a CTK chaos experiment.     |
| ```/verify_behav```     | ```GET```   |  | Returns the page where a transient behavior verification can be carried out in a stand-alone manner.     |


## JSON specification description:

* ```behavior_description``` An optional text field that allows the specification of a text description of the transient behavior. 
* ```specification``` A required text field containing the formal description of the behavior, which is either an MTL formula, where the symbols for the temporal operators are replaced with their names or a textual PSP definition created using the PSP Wizard tool. 
* ```specification_type``` A required text field specifying the type of the formal behavior specification, can be either ```mtl``` or ```psp```.
	
* ```future-mtl``` An optional field allowing to specify that a future-MTL formula has been defined in the ```specification``` field. By default, the prototype assumes that the specified behaviors are in past-MTL. Additionally, the field should only be used when ```specification_type``` is set to ```mtl```. 
	
* ```predicates_info``` A required array containing the information regarding the logical predicates in the formal behavior specification. The array contains objects of the following format: 
	* ```predicate_description``` An optional text field that allows the specification of a text description of the logical predicate.
	*    ```predicate_name``` A required text field containing the predicate name as it occurs in the formal specification above.
	*    ```predicate_logic``` A required text field containing the name of a logical function from a predefined selection of  Boolean operations provided by the prototype.
	*    ```predicate_comparison_value``` A text field containing a value used as the comparison value for the respective logical operation. Not all functions require the inclusion of this field, e.g., the ```boolean``` function and the trend functions. 

	
* ```measurement_source``` A required text field defining the source of the measurement data, currently supporting ```influx``` for InfluxDB, ```prometheus``` for Prometheus,```csv``` for local CSV files, and ```remote-csv``` for remote csv files, for example hosted on a web server.
	
* ```remote-csv-address``` Required when ```measurement_source``` is set to ```remote-csv```. This field contains the URL to the CSV table. 
	
* ```measurement_points``` A required array containing information regarding the measurement data. 
	
	* ```measurement_name``` A required text field containing the name of the measurement as it occurs in the behavior specification.
	* ```measurement_query``` A text field specifying the query that will be used to retrieve the data. Only required when ```measurement_source``` is specified as ```influx``` or ```prometheus```.
	* ```measurement_column``` A text field specifying the column from which the measurement data will be retrieved. Only required when ```measurement_source``` is set to ```csv``` or ```remote-csv```. 
	*    ```start_time``` A text field for specifying the start time of the query interval. Only required when ```measurement_source``` is set to ```prometheus```.
	*    ```end_time``` A text field for specifying the end time of the query interval. Only required when ```measurement_source``` is set to ```prometheus```.
	*    ```steps``` A text field for specifying the steps of the query interval. Only required when ```measurement_source``` is set to ```prometheus```.

