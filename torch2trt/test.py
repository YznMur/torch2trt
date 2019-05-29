from torch2trt import *
import torchvision
import time
import argparse


class ModuleTest(object):
    def __init__(self, module_fn, type, device, input_shapes, max_error=1e-2, **torch2trt_kwargs):
        self.module_fn = module_fn
        self.type = type
        self.device = device
        self.input_shapes = input_shapes
        self.max_error = max_error
        self.torch2trt_kwargs = torch2trt_kwargs
        
    def run(self):
        # create module
        module = self.module_fn()
        module = module.to(self.device)
        module = module.type(self.type)
        module = module.eval()
        
        # create inputs
        inputs = ()
        for shape in self.input_shapes:
            inputs += (torch.ones(shape).to(self.device).type(self.type), )

        # convert module
        module_trt = torch2trt(module, inputs, **self.torch2trt_kwargs)

        # test output against original
        outputs = module(*inputs)
        outputs_trt = module_trt(*inputs)

        if not isinstance(outputs, tuple):
            outputs = (outputs, )

        # compute max error
        max_error = 0
        for i in range(len(outputs)):
            max_error_i = torch.max(torch.abs(outputs[i] - outputs_trt[i]))
            if max_error_i > max_error:
                max_error = max_error
        
        # benchmark pytorch
        t0 = time.time()
        for i in range(50):
            outputs = module(*inputs)
        t1 = time.time()
        
        fps = 50.0 / (t1 - t0)
        
        # benchmark tensorrt
        t0 = time.time()
        for i in range(50):
            outputs = module_trt(*inputs)
        t1 = time.time()
        
        fps_trt = 50.0 / (t1 - t0)
        
        return max_error, fps, fps_trt
            
            
                
TESTS = {
    'alexnet_fp16_3x224x224': ModuleTest(torchvision.models.alexnet, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'squeezenet1_0_fp16_3x224x224': ModuleTest(torchvision.models.squeezenet1_0, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'squeezenet1_1_fp16_3x224x224': ModuleTest(torchvision.models.squeezenet1_1, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'resnet18_fp16_3x224x224': ModuleTest(torchvision.models.resnet18, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'resnet34_fp16_3x224x224': ModuleTest(torchvision.models.resnet34, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'resnet50_fp16_3x224x224': ModuleTest(torchvision.models.resnet50, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'resnet101_fp16_3x224x224': ModuleTest(torchvision.models.resnet101, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'resnet152_fp16_3x224x224': ModuleTest(torchvision.models.resnet152, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'densenet121_fp16_3x224x224': ModuleTest(torchvision.models.densenet121, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'densenet169_fp16_3x224x224': ModuleTest(torchvision.models.densenet169, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'densenet201_fp16_3x224x224': ModuleTest(torchvision.models.densenet201, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'densenet161_fp16_3x224x224': ModuleTest(torchvision.models.densenet161, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'vgg11_fp16_3x224x224': ModuleTest(torchvision.models.vgg11, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'vgg13_fp16_3x224x224': ModuleTest(torchvision.models.vgg13, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'vgg16_fp16_3x224x224': ModuleTest(torchvision.models.vgg16, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'vgg19_fp16_3x224x224': ModuleTest(torchvision.models.vgg19, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'vgg11_bn_fp16_3x224x224': ModuleTest(torchvision.models.vgg11_bn, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'vgg13_bn_fp16_3x224x224': ModuleTest(torchvision.models.vgg13_bn, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'vgg16_bn_fp16_3x224x224': ModuleTest(torchvision.models.vgg16_bn, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
    'vgg19_bn_fp16_3x224x224': ModuleTest(torchvision.models.vgg19_bn, torch.float16, torch.device('cuda'), [(1, 3, 224, 224)], max_error=1e-2, fp16_mode=True),
}


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', '-o', help='Test output file path', type=str, default='torch2trt_test.md')
    args = parser.parse_args()
    
    print('| Name | Max Error | FPS (PyTorch) | FPS (TensorRT) |')
    print('|------|-----------|---------------|----------------|')
    for name, test in TESTS.items():
        line = None
        try:
            max_error, fps, fps_trt = test.run()
            line = '| %s | %.3g | %.3g | %.3g |' % (name, max_error, fps, fps_trt)
        except:
            line = '| %s |    |    |    |' % name
        print(line)
        with open(args.output, 'a+') as f:
            f.write(line + '\n')