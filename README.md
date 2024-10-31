# Dagger Test

This is a sample project


## Delivering the Project

To deliver this project, you need to run the following steps:

* build the Java software (using gradle)
* do a code analysis using CodeQL
* package the Java software into a container image (using docker)
* scan the container image for known vulnerabilities (using trivy)


### Without Dagger

You can run all the delivery steps in your GitHub action pipeline, following a commit.

Locally, before the commit, you need to run the steps manually, after installing 5 pre-requisites:
```bash
java
gradle
codeql
docker (Rancher, Docker for Windows, etc.)
trivy
```


### With Dagger

Locally, before the commit, you can run all the delivery steps with a single command:
```bash
dagger run python3 ci.py
```
after installing 3 pre-requisite:
```bash
dagger language of choice (can be either: python, node, bash, etc.)
dagger.io
docker (Rancher, Docker fo Windows, etc.)
```
> See the dagger pipeline [ci.py](./ci.py)

In your GitHub action pipeline, you have minimal code (see [.github/workflows/main.yml](./.github/workflows/main.yml), 
which is running the same dagger pipeline.


## Using the Image
```bash
$ docker run -it IMAGENAME /app/mytest1-0.1/bin/mytest1

2024-04-01T07:24:43.641 [INFO] io.micronaut.context.DefaultApplicationContext$RuntimeConfiguredEnvironment - Established active environments: [cli]
Hi from mytest1!
```
