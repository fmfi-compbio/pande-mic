To install, please run
```
python3 install.py 
```
and follow the instructions

download a slightly modified version of deepnano blitz: https://github.com/janka000/deepnano-blitz  
and note the path where it is installed

IMPORTANT! - install deepnano blitz into the environment cretaed in previous step, NOT into a new one

Next, please run the example (no need to change any files, the pipeline has run-time check implemented and will detect non-existing paths and ask you to provide them):

```

cd example

python -u ../python/main.py --config_dir $PWD/example_config/

```
