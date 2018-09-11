# M33_NOEMA
Imaging and Analysis for the M33 CO(2-1) NOEMA Project

Imaging
-------

* Conversion from GILDAS/CLASS to CASA in `imaging/gildas_to_casa` **TODO: Describe this process in more detail for future use.**
* Imaging: Performed in CASA 4.7.2 using the [yclean](http://home.strw.leidenuniv.nl/~ycontreras//yclean.html). yclean performed better than the automasking built into CASA 5.1 (I didn't test on any newer versions, though I think this automask has been updated). The final cube is cleaned to 2-sigma (~0.44 K).
* Feathering: There is minimal overlap between these data (shortest baseline ~15m = 18") and the IRAM 30-m data (12"). Feathering does not improve the bowling and is probably unnecessary.
* uv-overlap: The NOEMA data *may* be in the same antenna temperature scale as the IRAM 30-m data. Applying the Tmb correction to the IRAM 30-m data leads to a ratio of ~0.6 in the overlapping uv-region. Without the Tmb conversion, the ratio is ~1.0. Still need to test whether this is actually the case.
* The 0.5 km/s data are highly correlated over ~2 channels (r~0.5). The effective velocity resolution is ~1.0 km/s. Rather than downsampling, the channel response can be forward-modeled for the analysis.
