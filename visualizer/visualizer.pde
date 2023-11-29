// https://github.com/una1veritas/Processing-sketches/blob/master/libraries/udp/examples/udp/udp.pde
import hypermedia.net.*;
import processing.net.*;

// dimensions to use for the processing canvas
int WIDTH = 1024 + 512;
int HEIGHT = 512 + 256;

// a UDP client to receive data
UDP data_udp;

// variables for configuring screen width
String message;
Server server;
Client client;

// a scaling factor, each LED is represented as a square of this size
int scale = 50;

// memory for the simulated pixels
int LEDS_WIDTH = 5;
int LEDS_HEIGHT = 5;
color[] leds = new color[LEDS_WIDTH * LEDS_HEIGHT];


void blankScreen() {
   // blank the screen
  fill(color(0, 0, 0));
  rect(0,  0, WIDTH, HEIGHT); 
}

void rescale(int leds_wide, int leds_high) {
  print("rescaling: (");
  print(leds_wide);
  print(", ");
  print(leds_high);
  println(")");

  // blank screen
  blankScreen();
  
  leds = new color[leds_wide * leds_high];
  LEDS_WIDTH = leds_wide;
  LEDS_HEIGHT = leds_high;
  
  // find the largest possible scale factor
  int sw = WIDTH / leds_wide;
  int sh = HEIGHT / leds_high;
  
  print(sw);
  print(" ");
  println(sh);
  
  // the smaller of the two scales is the largest possible
  if (sw < sh) {
    scale = sw;
  } else {
    scale = sh;
  }
}

void settings() {
  size(WIDTH, HEIGHT);
}

void setup() {
  noStroke();
 colorMode(RGB, 255, 255, 255);
  
  // set up UDP listener for data messages
  data_udp = new UDP( this, 6420 );
  //data_udp.log( true );
  data_udp.listen( true );
  
  server = new Server(this, 6969);
}

//process events
void draw() {
  blankScreen();
  //println(scale);
  for (int idx = 0; idx < LEDS_WIDTH; idx++) {
   for (int idy = 0; idy < LEDS_HEIGHT; idy++) {
    fill(color(leds[idy * LEDS_WIDTH + idx]));  // Use color variable 'c' as fill color
    rect( scale*idx,  scale*idy, scale, scale);  // Draw rectangle 
   }
  }

  // check for messages from clients
  client = server.available();
  if (client != null) {
    message = client.readString(); 
    message = message.substring(0, message.indexOf("\n"));

    // parse the supplied width and height
    int[] config = int(split(message, ' '));
    
    // rescale the output
    rescale(config[0], config[1]);
  }
}

 void receive( byte[] data ) {       // <-- default handler
//void receive( byte[] data, String ip, int port ) {  // <-- extended handler
    int bpp = 4;
    int pixels_received = data.length / bpp;
    int pixels_in_display = LEDS_WIDTH * LEDS_HEIGHT;
    
    int pix = pixels_received;
    if (pixels_received > pixels_in_display) {
      pix = pixels_in_display;
    }
    
    for (int idx = 0; idx < pix; idx++) {      
      leds[idx] = color(int(data[idx * bpp + 2]), int(data[idx * bpp + 1]), int(data[idx * bpp + 0]));
    }
}
