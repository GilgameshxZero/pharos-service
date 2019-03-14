# Pharos Service

Service accessible via mobile allowing job submission to the Pharos printing service at MIT.

Yang Yan, Stella Yang, Tony Wang, Jing lin

## Support

Service|File format|Options
|-|-|-|
Facebook messenger|PDF|Color; Two-sided
Email|PDF|Color; Two-sided
mitprint.to|PDF|Color; Two-sided

## System

Services are hosted on a Windows server on AWS, and all redirect to a common backend queue. The queue is processed with ghostscript and a Windows script to enter the Kerberos at the popup.
