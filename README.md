# GPU relative performance

This is a solution to a problem that if you probably have not
 even encountered if you are not running a multiple different
 GPU's in one way of another... of course, this package tries
 to solve that!
 
 # First world problems.
 
 Be it for Neural Network training or Mining you need to have
 a way to distribute the load equally to each GPU. For example
 although `mxnet` *supports* multiple GPU's the scheduler currently
 does *not* know the relative performance of each GPU available
 and either you have to do it by hand or a uniform load 
 distribution is applied to each GPU (more [here][1]).
 
 # The (quick) solution.
 
 Now, I've thought of how to tackle this problem with 
 micro-benchmarks, load measurements and so on... but I like
 the KISS principle and hence I am using something simple with
 minimal overhead which works surprisingly well in practice.
 Basically what I want to accomplish is to get a relative 
 performance of each GPU against the lowest performing one
 currently installed; this can be achieved by using 
 [Geekbench][2] aggregated CUDA benchmarks scores and construct
 a relative performance index for the currently installed GPU's.
 
 The main gist of this solution is fetch the raw `JSON` CUDA 
 benchmark data from Geekbench, parse it, find the GPU's 
 installed in the system while matching and normalizing their
 performance using the CUDA benchmark scores. These results
 can then be immediately used in the `mxnet` scheduler as
 percentages.
 
 # Requirements
 
  Currently this exists as a source distribution and requires `nvidia-smi`
 to be installed -- which if you are using an NVIDIA GPU with either
 Windows or Linux it should already be installed. Roughly, the requirements
 are as follows:
 
    * Python > 3
    * Nvidia Drivers
 
 Unfortunately, MacOS does not have `nvidia-smi` yet, but a workaround exists 
 which I will probably include in a future update.
 
 
 # Usage
 
 Using this package is easy, first of all do:
 
 ```
 $ pip install gpurelperf
```

Then, after install completes you can use it as a normal package:

```python
import gpurelperf

print(get_sys_cards())
```

# License

This project is licensed under the terms and conditions of the Apache 2.0 license.
 
 
[1]: https://mxnet.incubator.apache.org/how_to/multi_devices.html
[2]: https://browser.geekbench.com/cuda-benchmarks