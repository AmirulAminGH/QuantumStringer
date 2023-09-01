# QuantumStringer

Overall controller will have single motherboard(carrier) and 4 system on module boards
1. Raspberry pi as the main network handle and code pre-processor
2. Atmega2560 SOM as the main kineamtics controller
3. ESP32S3 as the feedback, inverse kinematics processing and error checking controller. The function is separated due to the limitation of 8=bit AVR controller.
4. Signal level shifter if 5v outpput signal is deemed to low to communicate over long distance(possible shift from 5v > 24v)

Further upgrade shall includes ugrading the 8-bit kinematics controller to 32 bit based controller with hardware abstraction layering(HAL), preferably using STM32 based - military grade(MILSTD300) MCU for robustness and reliability.



![image](https://github.com/AmirulAminGH/QuantumStringer/assets/87349346/6972d490-7628-4e12-a44a-e7eab52aa39e)
![image](https://github.com/AmirulAminGH/QuantumStringer/assets/87349346/c65689cb-12f6-4071-89c8-34bc3f88fe03)
22![image](https://github.com/AmirulAminGH/QuantumStringer/assets/87349346/f0b0ac25-4488-4eea-a497-605cd25a7891)
![image](https://github.com/AmirulAminGH/QuantumStringer/assets/87349346/4d55bf4d-dff1-4ad2-a9fb-2fcf4678bb5c)
![image](https://github.com/AmirulAminGH/QuantumStringer/assets/87349346/3159ae45-0ac3-41ba-8237-e15015d7f0a5)
![image](https://github.com/AmirulAminGH/QuantumStringer/assets/87349346/26af756e-a861-460c-80c0-01ec14b90923)
![image](https://github.com/AmirulAminGH/QuantumStringer/assets/87349346/0aece256-5d7f-4eca-af83-bb8218d59c22)
![image](https://github.com/AmirulAminGH/QuantumStringer/assets/87349346/c204cb84-2af2-46b7-821c-0260518d67c1)



