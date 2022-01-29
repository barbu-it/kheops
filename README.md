# Kheops


![Kheops Logo!](logo/kheops_brand.png "Kheops Logo")


## Introduction

> [~~Jerakia~~](https://web.archive.org/web/20180829194211/http://jerakia.io/documentation/)Kheops is a tool that performs key value lookups against a variety of pluggable data stores. It does this using a top-down hierarchical set of queries that allow you to define global values and override them at different levels of a configurable hierarchy.

> This has many use cases, including infrastructure management where you often have configuration values defined at a global level but wish to override these values based on certain factors such as the environment or location of the request.

Kheops is a fresh python rewrite of this project. It does not attempt to have the same features, and it's work in progress project.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Installing

Install Kheops

```
pip install kheops
```

And check it works:
```
kheops --help
```

Now you can test the examples, and learn how to use it [here](/lost).

```
kheops --config examples/01_simple/ hello   
kheops --config examples/01_simple/ hello -e site=
kheops --config examples/01_simple/ hello -e site=
```

## Learning Kheops








## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

### Development

Clone this git repository:
```
git clone ...
```

Create virtualenv and install poetry if not already done:
```
virtualenv -p python3 venv
. venv/bin/activate
pip install --upgrade pip poetry
```

Install Kheop with poetry:
```
poetry install
```

And check it works:
```
kheops --help
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc



A jerakia old website:
https://web.archive.org/web/20190209052035/http://jerakia.io/

https://web.archive.org/web/20180829194211/http://jerakia.io/documentation/



key-value configuration data lookup system


A VERSATILE DATA LOOKUP SYSTEM

Jerakia is a tool that performs key value lookups against a variety of pluggable data stores. It does this using a top-down hierarchical set of queries that allow you to define global values and override them at different levels of a configurable hierarchy.

This has many use cases, including infrastructure management where you often have configuration values defined at a global level but wish to override these values based on certain factors such as the environment or location of the request.

Kheops is a key-value configuration data lookup system. It can performs a key value lookup against a variety of data stores.
