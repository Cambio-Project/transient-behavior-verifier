# How to run it in a docker container:

1. Navigate to the src folder
2. Build the docker image:

```
docker build . -t transient-behavior-verifier
```

3. Run the container:

```
docker run -p 5000:5000 transient-behavior-verifier
```

4. You should now be able to access the web UI via localhost:5000

