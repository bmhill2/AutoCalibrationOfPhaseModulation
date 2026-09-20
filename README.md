This is a demonstration of automatic calibration of a QPSK transmitter using spectrum peak measurement techniques.
The main flowgraph is "AutoCalibrationQPSK_demo."  It was made with GNU Radio Companion v3.8.  

The heart of the automatic calibration is an embedded python block.  The code for this block is epy_block_0.py.

There are OOTs used to switch between different test signals and allow PMT messages to update relative gain values, 
quadrature skew, and DC offsets.
