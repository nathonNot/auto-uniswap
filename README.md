# Auto-deploying the swap contract

## Preconditions

node 18.x
python > 3.10.x

Set the private key to the environment variable PRIVATE_KEY

## Init

Git clone this project

```
chmod 777 init.sh
./init.sh
```

## Deploy the swap contract on cyber

```
python deploy.py cyber
```

## Deploy the swap contract on bitlayer

```
python deploy.py bitlayer
```

**Logs and deployment-related logs will be generated in the deploy_log and deploy_save directories of the current directory.**