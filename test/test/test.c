/*
 * test.c
 *
 * Created: 25-12-2018 15:08:24
 *  Author: Swaraj
 */
 #define F_CPU 14745600
 #include <avr/io.h>
 #include <avr/interrupt.h>
 #include <util/delay.h>
 #include <string.h>

 #define RX  (1<<4)
 #define TX  (1<<3)
 #define TE  (1<<5)
 #define RE  (1<<7)

 volatile unsigned char data;
 unsigned char LEFT = 0,RIGHT = 0,MIDDLE = 0;
 int middle = 0,left = 0, right = 0,M = 0,R = 0,L = 0;

void uart0_init()
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

void adc_pin_config (void)
{
	DDRH = 0x01;
	PORTH = 0x00;

	DDRF = 0x00;
	PORTF = 0x00;
	DDRK = 0x00;
	PORTK = 0x00;
}

void adc_init()
{
	ADCSRA = 0x00;
	ADCSRB = 0x00;		//MUX5 = 0
	ADMUX = 0x20;		//Vref=5V external --- ADLAR=1 --- MUX4:0 = 0000
	ACSR = 0x80;
	ADCSRA = 0x86;		//ADEN=1 --- ADIE=1 --- ADPS2:0 = 1 1 0
}

//Function For ADC Conversion
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

void Led_init(void)
{
	DDRJ = 0b00001111;
	PORTJ = 0b00000000;
}

void Read_path(void)
{
	static int left = 0 , right = 0 , middle = 0 ;
	static count = 0 ;
	static char scl[20] ;
	left = ADC_Conversion(3);
	middle = ADC_Conversion(1);
	right = ADC_Conversion(2);
	if(left >= 206)		//Sets L 1 if senses black line under the left sensor else 0. prev value 240
	{
		L = 1;
		PORTJ = (0b11111110) & PORTJ;
	}
	else
	{
		L = 0;
		PORTJ = (0b00000001) | PORTJ;
	}
	if(right >= 214)		//Sets R 1 if senses black line under the left sensor else 0.
	{
		R = 1;
		PORTJ = (0b11111011) & PORTJ;
	}
	else
	{
		R = 0;
		PORTJ = (0b00000100) | PORTJ;
	}
	if(middle >= 188)	//Sets M 1 if senses black line under the left sensor else 0. prev value 238
	{
		M = 1;
		PORTJ = (0b11111101) & PORTJ;
	}
	else
	{
		M = 0;
		PORTJ = (0b00000010) | PORTJ;
	}
	/*if(ShaftCountLeft > 410)
	{
		PORTJ = 0b00001000 | PORTJ;
	}
	else
	{
		PORTJ = 0b11110111 & PORTJ;
	}*/
}

int main(void)
{	int l=0,i;
	char L[20],R[20],M[20];
	adc_pin_config();
	uart0_init();
	adc_init();
	Led_init();
	UCSR0B |= (1 << RXCIE0);
	sei();
    while(1)
    {
		Read_path();
        LEFT = ADC_Conversion(3);
		MIDDLE = ADC_Conversion(1);
		RIGHT = ADC_Conversion(2);
		snprintf( L, 20 , "%d", LEFT );
		if(LEFT >= 100)
		{
			for(i=0;i != 3;i++)
			{
				uart_tx(L[i]);
			}
			uart_tx('_');
		}	
		else if(LEFT >= 10)
		{
			for(i=0;i != 2;i++)
			{
				uart_tx(L[i]);
			}
			uart_tx('_');
		}
		else
		{
			for(i=0;i != 1;i++)
			{
				uart_tx(L[i]);
			}
			uart_tx('_');
		}			
		snprintf( M, 20 , "%d", MIDDLE );
		if(LEFT >= 100)
		{
			for(i=0;i != 3;i++)
			{
				uart_tx(M[i]);
			}
			uart_tx('_');
		}
		else if(MIDDLE >= 10)
		{
			for(i=0;i != 2;i++)
			{
				uart_tx(M[i]);
			}
			uart_tx('_');
		}
		else
		{
			for(i=0;i != 1;i++)
			{
				uart_tx(M[i]);
			}
			uart_tx('_');
		}
		snprintf( R, 20 , "%d", RIGHT );
		if(LEFT >= 100)
		{
			for(i=0;i != 3;i++)
			{
				uart_tx(R[i]);
			}
		}
		else if(RIGHT >= 10)
		{
			for(i=0;i != 2;i++)
			{
				uart_tx(R[i]);
			}
		}
		else
		{
			for(i=0;i != 1;i++)
			{
				uart_tx(R[i]);
			}
			uart_tx('_');
		}
		_delay_ms(500);
    }
}