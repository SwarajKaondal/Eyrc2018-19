/*
*Team Id :	   783
*Author List : Swaraj kaondal
 			   Shubham kakirde
 			   Pratyush Kaware
  			   Vedant Kayande
*File Name :   AVR_Progress_task
*Theme :	   Thirsty_Crow
*Functions :   buzzer_pin_config, motor_pin_config, forward, backward, left, right, soft_left, soft_right, stop, uart0_init, uart_tx, adc_pin_config,
			   adc_init, ADC_Conversion, Read_path, uart_rx, Rotate_pie, left_encoder_pin_config, left_position_encoder_interrupt_init , main.
*Global Variables : i, previous_i, LEFT, RIGHT, MIDDLE, ShaftCountLeft, L, R, M, flag, data[70]	
*/		   

#define F_CPU 14745600
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>


#define RX  (1<<4)
#define TX  (1<<3)
#define TE  (1<<5)
#define RE  (1<<7)


/*---------------------------------------------------Declaring an array to store movement instructions--------------------------------------*/

uint8_t data[70];

/*----------------------------------------------------Declaring global variables------------------------------------------------------------*/

int i = 0 , previous_i = -1 ;
long int ShaftCountLeft = 0;
char Rotate_left_right_G = 'A';
int L , R , M , flag = 0 , f = 0 , f1 = 0 ,slow_flag = 0;
char last_reading = 'l';
unsigned int timeout_ctr = 0 ;


/*
Function Name : magnet_pin_config
Input :			None
Output :		Initializes the magnet Port.
Logic :			Sets the port B.
Example Call :  magnet_pin_config();
*/
void Led_init(void)
{
	DDRJ = 0b00001111;
	PORTJ = 0b00000000;
}
void magnet_pin_config(void)
{
	DDRH = 0b00000001;
	PORTH = 0b00000000;
}
/*
Function Name : magnet_on
Input :			None
Output :		Switches the magnet on.
Logic :			Sets the port B.
Example Call :  magnet_on();
*/
void magnet_on(void)
{
	PORTH = 0b00000001;
}

/*
Function Name : magnet_off
Input :			None
Output :		Switches the magnet off.
Logic :			Sets the port B.
Example Call :  magnet_off();
*/
void magnet_off(void)
{
	PORTH = 0b00000000;
}
/*
Function Name : buzzer_pin_config()
Input :			None
Output :		Initializes the buzzer port.
Logic :			Sets the port B.
Example Call :  buzzer_pin_config();
*/
void buzzer_pin_config(void)
{
	DDRB = 0b00000001;
	PORTB = 0b00000000;
}

/*
Function Name : motor_pin_config()
Input :			None
Output :		Initializes the motor port.
Logic :			Sets the port A.
Example Call :  motor_pin_config();
*/
void motor_pin_config(void)
{
	DDRA = 0b11111111;
	PORTA = 0b00000000;
}

/*
Function Name : backward()
Input :			None
Output :		Moves the Bot backward.
Logic :			Done by moving both the motors in backward direction.
Example Call :  backward();
*/

void backward(void)
{
	PORTA = 0b01001101 ;
	{
		_delay_ms (8) ;
	}	
	PORTA = 0b00000000;
	_delay_ms(30);
}

/*
Function Name : forward()
Input :			None
Output :		Moves the Bot forward.
Logic :			Done by moving both the motors in forward direction.
Example Call :  forward();
*/
void forward(void)
{
	timeout_ctr = 0 ;
	PORTA = 0b10001110;
	
	if(data[i+1] == 3)
	{
		_delay_ms(6);
	}
	else if((data[i] == 2) || (slow_flag == 1) || (i == -1))
	{
		_delay_ms (8);
	}
	else if ( ( (slow_flag == 0) && (data[i+1] != 6) ) && ShaftCountLeft >= 200)
	{
		_delay_ms (14) ;
	}
	else if( ShaftCountLeft < 200 && (slow_flag == 0) && (data[i+1] != 6)) 
	{
		_delay_ms (10) ;
	}
	else
	{
		if(ShaftCountLeft >= 200)
		{
			_delay_ms(10);
		}
		else
		{
			_delay_ms(8);
		}
	}
	PORTA = 0b00000000 ;
	_delay_ms ( 40 ) ;
}

/*
Function Name : left()
Input :			None
Output :		Bot takes a hard left.
Logic :			Done by moving the left motor backward and right motor in forward direction.
Example Call :  left();
*/
void left(void)
{
	timeout_ctr = 0 ;
	ShaftCountLeft = 0 ;
	PORTA = 0b10001101;
	if(data[i+1] == 3)
	{
		_delay_ms (6);
	}
	else
	{
		_delay_ms (9) ;
	}
	PORTA = 0b00000000;
	_delay_ms ( 43 ) ;
}

/*
Function Name : right()
Input :			None
Output :		Bot takes a hard right.
Logic :			Done by moving the left motor forward and right motor in backward direction.
Example Call :  right();
*/
void right(void)
{
	timeout_ctr = 0 ;
	ShaftCountLeft = 0 ;
	PORTA = 0b01001110;
	if(data[i+1] == 3)
	{
		_delay_ms (6);
	}
	else
	{
		_delay_ms (9) ;
	}
	PORTA = 0b00000000;
	_delay_ms ( 43 ) ;
}

/*
Function Name : soft_right()
Input :			None
Output :		Bot takes a soft right.
Logic :			Done by moving the left motor forward and stopping the right motor.
Example Call :  soft_right();
*/
void soft_right(void)
{
	timeout_ctr ++ ;
	PORTA = 0b00001110;
	
	
	if(data[i+1] == 3)
	{
		_delay_ms(6);
	}
	else if((data[i] == 2) || (slow_flag == 1) || (i == -1))
	{
		_delay_ms (8);
	}
	else if ( ( (slow_flag == 0) && (data[i+1] != 6) ) && ShaftCountLeft >= 200)
	{
		_delay_ms (14) ;
	}
	else if( ShaftCountLeft < 200 && (slow_flag == 0) && (data[i+1] != 6))
	{
		_delay_ms (10) ;
	}
	else
	{
		if(ShaftCountLeft >= 200)
		{
			_delay_ms(14);
		}
		else
		{
			_delay_ms(10);
		}
	}
	
	
	
	
	/*if((data[i+1] == 3) || (data[i] == 2) || (slow_flag == 1) )
	{
		_delay_ms (6);
	}
	else if ( ShaftCountLeft >= 200)
	{
		_delay_ms (11) ;
	}
	else
	{
		_delay_ms (7) ;
	}*/
	PORTA = 0b00000000;
	_delay_ms ( 43 ) ;
}

/*
Function Name : soft_left()
Input :			None
Output :		Bot takes a soft left.
Logic :			Done by stopping the left motor and moving the right motor in forward direction.
Example Call :  soft_left();
*/
void soft_left(void)
{
	timeout_ctr ++ ;
	PORTA = 0b10001100;
	
	
	
	
	if(data[i+1] == 3)
	{
		_delay_ms(6);
	}
	else if((data[i] == 2) || (slow_flag == 1) || (i == -1))
	{
		_delay_ms (8);
	}
	else if ( ( (slow_flag == 0) && (data[i+1] != 6) ) && ShaftCountLeft >= 200)
	{
		_delay_ms (14) ;
	}
	else if( ShaftCountLeft < 200 && (slow_flag == 0) && (data[i+1] != 6))
	{
		_delay_ms (10) ;
	}
	else
	{
		if(ShaftCountLeft >= 200)
		{
			_delay_ms(14);
		}
		else
		{
			_delay_ms(10);
		}
	}
	
	
	
	
	/*if((data[i+1] == 3) || (data[i] == 2) || (slow_flag == 1) )
	{
		_delay_ms (6);
	}
	else if ( ShaftCountLeft >= 200)
	{
		_delay_ms (11) ;
	}
	else
	{
		_delay_ms (7) ;
	}*/
	PORTA = 0b00000000;
	_delay_ms ( 43 ) ;
	
}

/*
Function Name : stop()
Input :			None
Output :		Bot stops.
Logic :			Done by stopping both the motors.
Example Call :  stop();
*/
void stop(void)
{
	timeout_ctr = 0 ;
	PORTA = 0b00001100;
}

/*
Function Name : uart0_init()
Input :			None
Output :		Initializes uart communication.
Logic :			Done by setting the UCSR registers.
Example Call :  uart0_init();
*/
void uart0_init(void)
{
	UCSR0B = 0x00;							//disable while setting baud rate
	UCSR0A = 0x00;
	UCSR0C = 0x06;
	UBRR0L = 0x5F; 							//9600BPS at 14745600Hz
	UBRR0H = 0x00;
	//UCSR0B = 0x98;							//setting 8-bit character and 1 stop bit
	UCSR0B = RX | TX;
	UCSR0C = 3<<1;
}

/*
Function Name : uart_tx()
Input :			A character that has to be transmitted.
Output :		transmits 1 byte of data.
Logic :			Done by checking the TE flag continuously to verify whether the UDR0 register is available for use and sending data accordingly .
Example Call :  uart_tx('i');
*/
void uart_tx(char data)
{
	while(!(UCSR0A & TE));	//waiting to transmit
	if(data == '\n')
	{
		UDR0 = 0x0d;
	}
	else
	{
		UDR0 = data;
	}
}

/*
Function Name : adc_pin_config()
Input :			None
Output :		Configures the ADC registers.
Logic :			Done by setting Port F.
Example Call :  adc_pin_config();
*/
void adc_pin_config (void)
{
	DDRF = 0x00;
	PORTF = 0x00;
	DDRK = 0x00;
	PORTK = 0x00;
}

/*
Function Name : adc_init()
Input :			None
Output :		Initializes ADC.
Logic :			Done by setting the ADC registers.
Example Call :  adc_init();
*/

void adc_init(void)
{
	ADCSRA = 0x00;
	ADCSRB = 0x00;		//MUX5 = 0
	ADMUX = 0x20;		//Vref=5V external --- ADLAR=1 --- MUX4:0 = 0000
	ACSR = 0x80;
	ADCSRA = 0x86;		//ADEN=1 --- ADIE=1 --- ADPS2:0 = 1 1 0
}


/*
Function Name : ADC_Conversion()
Input :			Pin number that can be accessed by the ADC block.
Output :		Converts analog value to digital value, returns a digital value.
Logic :			Done by passing the data to the ADC block.
Example Call :  ADC_Conversion(1);
*/
unsigned char ADC_Conversion(unsigned char Ch)
{
	int a;
	if(Ch>7)
	{
		ADCSRB = 0x08;
	}
	
	Ch = Ch & 0x07;
	ADMUX= 0x20| Ch;
	ADCSRA = ADCSRA | 0x40;		//Set start conversion bit
	while((ADCSRA&0x10)==0);	//Wait for conversion to complete
	a=ADCH;
	ADCSRA = ADCSRA|0x10; //clear ADIF (ADC Interrupt Flag) by writing 1 to it
	ADCSRB = 0x00;
	return a;
}

/*
Function Name : Read_path()
Input :			None
Output :		Sets the L,M,R variables which indicate whether the state of the bot in accordance to the black line.
Logic :			The data is first passed to the ADC_Concersion function which returns a digital value. Further these values are
				used to set the L,M,R on comparing with the threshold values of the left, middle and the right sensor ,which define the
				state of the bot.
Example Call :  Read_path();
*/
void Read_path(void)
{
	static int LEFT = 0 , RIGHT = 0 , MIDDLE = 0 ;
	static count = 0 ;
	static char scl[20] ;
	LEFT = ADC_Conversion(3);
	MIDDLE = ADC_Conversion(1);
	RIGHT = ADC_Conversion(2);
	if(LEFT >= 206)		//Sets L 1 if senses black line under the left sensor else 0. prev value 240
	{
		L = 1;
		PORTJ = (0b11111110) & PORTJ;
	}
	else
	{
		L = 0;
		PORTJ = (0b00000001) | PORTJ;
	}
	if(RIGHT >= 214)		//Sets R 1 if senses black line under the left sensor else 0.
	{
		R = 1;
		PORTJ = (0b11111011) & PORTJ;
	}
	else
	{
		R = 0;
		PORTJ = (0b00000100) | PORTJ;
	}
	if(MIDDLE >= 188)	//Sets M 1 if senses black line under the left sensor else 0. prev value 238
	{
		M = 1;
		PORTJ = (0b11111101) & PORTJ;
	}
	else
	{
		M = 0;
		PORTJ = (0b00000010) | PORTJ;
	}
	if( slow_flag == 1 )
	{
		f1 = 0 ;
		PORTJ = 0b00001000 | PORTJ;
	}
	else
	{
		PORTJ = 0b11110111 & PORTJ;
	}
}
/*
Function Name : uart_rx()
Input :			None
Output :		1 byte Character received on register UDR0.
Logic :			Done by checking the RE flag continuously to verify whether the UDR0 register has received some data or not.
Example Call :  uart_rx();
*/
char uart_rx()
{
	while(!(UCSR0A & RE));				//waiting to receive.
	return UDR0;
}

/*
Function Name : Rotate_pie()
Input :			None.
Output :		Rotates the bot by 180 degrees.
Logic :			(When this function is called the bot will always be right above the node facing away from the black line.)
				When the bot is right above the node, the bot is made to turn left and continuously read path while turning left until a black line is
				sensed by the bot.This is done by turning left until right sensor senses the black line. At this point the bot has rotated by 60 degrees. 
				The bot is moved a little bit back to keep it on the track, again the bot is rotated left till the right sensor is above the black line. Further 
				the bot keeps rotating left until the left sensor senses the black line at this point the bot has rotated through 180 degrees.
Example Call :  Rotate_pie();
*/
void Rotate_pie(void)
{
	int j;
	if(data[i+1] == 3)
	{
		PORTA = 0b10001110 ;  //forward
		_delay_ms ( 10 ) ;
		PORTA = 0b00000000 ;
	}
	if(data[i] == 2)
	{
		while(!R)
		{
			left();
			Read_path();
		}
		for(j = 0;j < 6; j++)
		{
			backward();
		}	
		while(R || M)
		{
			Read_path();
			left();
		}
		while( !M )
		{
			Read_path();
			left();
		}
		if(data[i+1] != 3)
		{
			PORTA = 0b01001101 ;
			_delay_ms ( 10 ) ;
			PORTA = 0b00000000 ;
		}
	}
	else
	{
		while(!L)
		{
			right();
			Read_path();
		}
		for(j = 0;j < 6; j++)
		{
			backward();
		}
		while(L || M)
		{
			Read_path();
			right();
		}
		while( !M )
		{
			Read_path();
			right();
		}
		if(data[i+1] != 3)
		{
			PORTA = 0b01001110 ;
			_delay_ms ( 10 ) ;
			PORTA = 0b00000000 ;
		}
	}		
}

/*
Function Name : Pebble_pick_n_drop()
Input :			The amount of distance it has to move to pickup or drop the pebble.
Output :		It makes the robot pick or drop the pebble after detecting the desired node.
Logic :			The static variable checks whether its a pebble drop or pebble pickup. Accordingly it switches magnet on or off.
				It checks the left motor encoder whether it has rotated enough or not to cover the given distance.
Example Call :  Pebble_pick_n_drop( distance ).
*/
void Pebble_pick_n_drop( int distance )
{
	static int Pebble_or_pitcher = 0;
	Pebble_or_pitcher++; 
	if(Pebble_or_pitcher % 2 != 0)
	{
		magnet_on();
	}
	ShaftCountLeft = 0 ;
	while ( ( ShaftCountLeft ) < distance )
	{
		forward();
	}
	if(Pebble_or_pitcher % 2 == 0)
	{
		magnet_off();
	}
	uart_tx('M');		//Sending M to change the pebble or Pitcher.
	_delay_ms(2000);
	
	ShaftCountLeft = 0 ;
	if( (data[i+1] == 2) || (data[i + 1] == 6) )
	{
		while ( ShaftCountLeft < distance + 25 )
		{
			backward();
		}
	}		
	else
	{
		while ( ShaftCountLeft < distance + 35 )
		{
			backward();
		}
	}
	
	ShaftCountLeft = 0 ;
}

/*
Function Name : left_encoder_pin_config()
Input :			None
Output :		Initializes Port B for encoder interrupt.
Logic :			Sets the Port B
Example Call :  left_encoder_pin_config();
*/

void left_encoder_pin_config (void)
{
	DDRB  = 0b11001111;
}

/*
Function Name : left_position_encoder_interrupt_init()
Input :			None
Output :		Initializes the interrupt for left motor encoder.
Logic :			Clears the global interrupt , configures the external interrupt 5 and enables the global interrupt.
Example Call :  left_position_encoder_interrupt_init();.
*/

void left_position_encoder_interrupt_init (void) //Interrupt 1 enable
{
	cli(); //Clears the global interrupt
	EICRB = EICRB | 0x08;//Configuring INT5 to give interrupt on falling edge
	EIMSK = EIMSK | 0x20;//Enabling INT5
	sei(); // Enables the global interrupt
}



//ISR for left position encoder
ISR(INT5_vect)
{
	ShaftCountLeft++;  //increment left shaft position count
}



/*
Function Name : main()
Input :			None
Output :		Makes the bot to execute all the instructions.
Logic :			It takes the instruction array by using the uart_rx function and iterates through the instruction and executes it.
Example Call :  Called automatically by the OS.
*/
int main(void)
{
	uint8_t j,Counter,No_of_beeps;  //Counter maintains the count of how many times it ringed the buzzer.
	char m;
	static int dist = 0 ;
	Led_init();
	uart0_init();
	adc_init();
	adc_pin_config();
	magnet_pin_config();
	motor_pin_config();
	buzzer_pin_config();
	left_encoder_pin_config();
	left_position_encoder_interrupt_init();
	uart_tx('R'); //Ready signal to start execution after switching on the bot.
	

	
	while(1)
	{
		m = uart_rx();
		if(UDR0 == 0b01000001) //0b01000101(ascii value of A) Instruction to rotate 180 degree.
		{
			data[i] = 2;		//Storing 2 in data array for 180 degree rotation.
			i++;
			continue;
		}
		if(UDR0 == 0b01000011) //0b01000101(ascii value of C) Instruction to rotate 180 degree.
		{
			data[i] = 5;		//Storing 5 in data array for 180 degree rotation.
			i++;
			continue;
		}
		if(UDR0 == 0b01010011) //0b01000101(ascii value of S) Instruction to slow down bot.
		{
			data[i] = 6;		//Storing 6 in data array to slow down bot.
			i++;
			continue;
		}
		if(UDR0 == 0b01001101)	//0b01001101(ascii value of M) Instruction to ring the buzzer.
		{
			data[i] = 3;		//Storing 3 in data array for ringing the buzzer.
			i++;
			continue;
		}
		
		if(UDR0 == 0b01001100)	//0b01001100(ascii value of L) Instruction to take left turn.
		{
			data[i] = 0;		//Storing 0 in data array to take a left turn.
			i++;
			continue ;
		}
		
		if(UDR0 == 0b01010010) //0b01010010(ascii value of R) Instruction to right turn.
		{
			
			data[i] = 1;		//Storing 1 in data array to take a right turn.
			i++;
			continue ;
		}
		if(UDR0 == 0b01011000)	//0b01011000(ascii value of X) Instruction to indicate the end.
		{
			data[i] = 4;		//Storing 4 in data array to end the execution.
		}
		
		if(data[i] == 4)	//Condition to check whether it has received all the instructions.
		{
			i = -1;			//Setting the index 'i' -1 as it increments the value of i further.
			if(data[i+1] == 6)
			{
				i = 0 ;
				slow_flag = 1 ;
			} 
			while(1)
			{
				f1 = 0 ;
				Read_path();				//Read path function sets variables L,M,R.
				if ( (L)&&(M)&&(R) )		//(111)for the condition : left=black  middle=black right=black 
				{
					
					if ( i == -1 )
					{
						while ( (L)&&(M)&&(R) )
						{
							
							Read_path();
							forward() ;
						}
					}
					else 
					{
						while ( ! ( (!L)&&(!M)&&(!R) ) )
						{
							Read_path();
							forward() ;						
						}
					}					
				}
				if( ((L)&&(M)&&(!R)) /*&& ( ShaftCountLeft <= 200)*/ ) 			//(110)for the condition : left=black  middle=black right=white (take left)
				{
					f1 = 1 ;
					//last_reading ='l';
					while ((L)&&(M)&&(!R) && timeout_ctr < 250 )
					{
						
						Read_path();
						soft_left () ;
					}
					if ( timeout_ctr >= 250)
					{	
						goto x ;
					}
					
					
				}
				else if (((L)&&(M)&&(!R)) /*&& ( ShaftCountLeft > 200)*/ ) 
				{
				//	last_reading ='l';
					while ((L)&&(M)&&(!R))
					{
						Read_path();
						forward () ;
					}	
					PORTA = 0b01001101 ;
					_delay_ms ( 10 ) ;
					PORTA = 0b00000000 ;
					/*if ( flag == 0 )
					{
						flag = 1 ;			//*set flag to 1*
					}	*/				
				}
									
				if((L)&&(!M)&&(R))			//(101)for the condition : left=black  middle=white right=black 
				{
					while ( ! ( (!L)&&(!M)&&(!R) ) )
					{
						Read_path();
						forward() ;
					}
				}
				
				if( ((L)&&(!M)&&(!R)) /*&& ( ShaftCountLeft <= 200)*/ )			//(100)for the condition : left=black  middle=white right=white
				{
					//last_reading ='l';
					
					while ((L)&&(!M)&&(!R) && timeout_ctr < 100 )
					{
						
						Read_path();
						soft_left();
					}
					if ( timeout_ctr >= 100)
					{
						
						goto x ;
					}
					
				}
				/*else if ( ((L)&&(!M)&&(!R))/*&& ( ShaftCountLeft > 200))
				{
					last_reading ='l';
					while ((L)&&(!M)&&(!R))
					{
						Read_path();
						forward () ;
					}
					PORTA = 0b01001101 ;
					_delay_ms ( 10 ) ;
					PORTA = 0b00000000 ;
					/*if ( flag == 0 )
					{
						flag = 1 ;			//*set flag to 1*
					}
				}*/
				
				if ( ((!L)&&(M)&&(R)) /*&& ( ShaftCountLeft <= 200)*/ )			//(011)for the condition : left=white  middle=black right=black
				{
					f1 = 1 ;
					//last_reading ='r';
					while ((!L)&&(M)&&(R) && timeout_ctr < 100)
					{
						
						Read_path();
						soft_right () ;
					}
					if ( timeout_ctr >= 100)
					{
						
						goto x ;
					}
					
				}
				/*else if ( ((!L)&&(M)&&(R)) && /*( ShaftCountLeft > 200) )
				{
					last_reading ='r';
					while ((!L)&&(M)&&(R))
					{
						Read_path();
						forward () ;
					}
					PORTA = 0b01001101 ;
					_delay_ms ( 10 ) ;
					PORTA = 0b00000000 ;
					/*if ( flag == 0 )
					{
						flag = 1 ;			//*set flag to 1*
					}
				}*/
				
				if ((!L)&&(M)&&(!R))		//(010)for the condition : left=white  middle=black right=white
				{
					while ((!L)&&(M)&&(!R))
					{
						Read_path();
						forward () ;
					}

					if ( flag == 0 )
					{
						flag = 1 ;			//*set flag to 1*
					}
										
				}
				
				if ( ((!L)&&(!M)&&(R)) /*&& ( ShaftCountLeft <= 200)*/ )		//001for the condition : left=white  middle=white right=black
				{
					//last_reading ='r';
					
					while ((!L)&&(!M)&&(R) && timeout_ctr < 250 )
					{
						
						Read_path();
						soft_right () ;
					}
					if ( timeout_ctr >= 250 )
					{
						
						goto x ;
					}
					
				}
				/*else if ( ((!L)&&(!M)&&(R)) && ( ShaftCountLeft > 200) )
				{
					last_reading ='r';
					while ((!L)&&(!M)&&(R))
					{
						Read_path();
						forward () ;
					}
					PORTA = 0b01001101 ;
					_delay_ms ( 10 ) ;
					PORTA = 0b00000000 ;
					/*if ( flag == 0 )
					{
						flag = 1 ;			//set flag to 1*
					}
				}
				*/
				
				if ((!L)&&(!M)&&(!R))		//000for the condition : left=white  middle=white right=white
				{
					while((!L)&&(!M)&&(!R))
					{
						Read_path();
						x:
						if( (f == 0) && ((ShaftCountLeft >= dist ) || (data[i] == 2)))	//flag will only be 1 if it has experienced the condition (010) left=white  middle=black right=white
						{
							if ( dist == 0 )
								dist = 250 ;
							i++;			//increment the index.
							if(data[i] == 6)
							{
								while(data[i] == 6)
								{
									slow_flag = 1;
									i++;
								}
							}								
							else
							{
								slow_flag = 0;
							}
							//PORTB = 0b00000001;
							PORTA = 0b01001101;
							if((data[i+1] == 3) || (data[i] == 3))
							_delay_ms(5);
							else
							_delay_ms(10);
							PORTA = 0b00000000;
							if((data[i+1] == 3) || (data[i] == 3))
							_delay_ms(95);
							else
							_delay_ms(90);
							//PORTB = 0b00000000;
							ShaftCountLeft = 0 ;
							f = 1 ;
						}
						
						
						if ( i != previous_i )		//Condition to execute an instruction only once.
						{
													
							previous_i = i ;
							f = 1 ;
							switch(data[i])
							{
								case 1:						//1 stands for right
									while(  (!R && !M) ) 
										{
											Read_path();
											right();
										}
										last_reading ='l';
										PORTA = 0b10001101;
										_delay_ms ( 10 ) ;
										PORTA = 0b00000000;
										stop();
										ShaftCountLeft = 0;
										flag = 0;		//flag set to 0(it will be again set to 1 only for the condition (010) left=white  middle=black right=white)
									break;
								case 0:							//0 stands for left
									while( (!L) )
										{
											Read_path();
											left();
										}
										last_reading ='r';
										PORTA = 0b01001110;
										_delay_ms ( 10 ) ;
										PORTA = 0b00000000;
										stop();
										ShaftCountLeft = 0;
										flag = 0;
									break;
								case 2 :						//2 stands for rotating by 180 degrees.
									//angle_rotate(9300);
									Rotate_pie();
									flag = 0;
									break;
								case 5:
									Rotate_pie();
									flag = 0;
									break;
								case 3:						//3 stands for ringing the buzzer.
									//delay_ms(1000);
									i++ ;
									if(data[i] == 6)
									{
										while(data[i] == 6)
										{
											slow_flag = 1;
											i++;
										}
									}
									else
									{
										slow_flag = 0;
									}
									//PORTB = 0b00000001;
									_delay_ms(100);
									//PORTB = 0b00000000;
									flag = 0; 
									Pebble_pick_n_drop( 150 );
									break;
						
								case 4:						//All instructions have been executed
										PORTB = 0b00000001;
										_delay_ms(5000);
										PORTB = 0b00000000;									
									return;
							}
						}	
						
						/*if ( ( i == previous_i) && ( data[previous_i] != 4 ) && ( f == 0 ) )
						{
							{	
								Read_path() ;
								if ( last_reading =='r' )
									left() ;
								else
									right() ;
								PORTJ = 0b00001000 | PORTJ;
							}							
						}
						PORTJ = 0b11110111 & PORTJ;
						*/
					}
					
					f = 0 ;
					
				}
			}
		}	
	}
	return 0;
}