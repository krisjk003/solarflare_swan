#include "xcnn_forward.h"

XCnn_forward_Config XCnn_forward_ConfigTable[] __attribute__ ((section (".drvcfg_sec"))) = {

	{
		"xlnx,cnn-forward-1.0", /* compatible */
		0x40000000 /* reg */
	},
	 {
		 NULL
	}
};