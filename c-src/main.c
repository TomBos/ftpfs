#include <stdio.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>

#include "structs.h"
#include "sock_utils.h"

#define ARUGMENT_ERROR 1
#define SOCK_CREATION_ERROR 2
#define HOST_CONNECTION_ERROR 3
#define HAND_SHAKE_ERROR 4

int main(int argc, char *argv[]) {
	if (argc < 3) {
        fprintf(stdout, "Usage: %s <server> <port>\n", argv[0]);
        return ARGUMENT_ERROR;
    }

	SocketContext ctx = {
		.sockfd = -1,
		.max_retries = 3
    };

	// create master socket
	if (!create_tcp_socket(&ctx)) {
        fprintf(stdout, "Failed to create socket after retries\n");
        return SOCK_CREATION_ERROR;
    }

	// get server and port
	char *server = argv[1];
	char *port_str = argv[2];
	int port = atoi(port_str);

	if (!connect_to_host(&ctx, server, port)) {
		fprintf(stdout, "Failed to connect to host\n");
		return HOST_CONNECTION_ERROR;
	}

	// create arrays to store messages
	char send_msg[BUFFER_SIZE];
	char recv_msg[BUFFER_SIZE];
	
	// Read initial response
	if (!recv_buff(&ctx, recv_msg, BUFFER_SIZE)) {
		fprintf(stdout, "Failed to read handshake\n");
		return HAND_SHAKE_ERROR;
	}


	// Send username
	snprintf(send_msg, BUFFER_SIZE, "USER %s\r\n", argv[3]);
	if (!send_buff(&ctx, send_msg)) {
		fprintf(stdout, "Failed to read send message\n");
		return 5;
	}
	if (!recv_buff(&ctx, recv_msg, BUFFER_SIZE)) {
		fprintf(stdout, "Failed to read handshake\n");
		return HAND_SHAKE_ERROR;
	}


	// Send password
	snprintf(send_msg, BUFFER_SIZE, "PASS %s\r\n", argv[4]);
	if (!send_buff(&ctx, send_msg)) {
		fprintf(stdout, "Failed to read send message\n");
		return 7;
	}
	if (!recv_buff(&ctx, recv_msg, BUFFER_SIZE)) {
		fprintf(stdout, "Failed to read handshake\n");
		return HAND_SHAKE_ERROR;
	}

	
	// Enter passive mode
	snprintf(send_msg, BUFFER_SIZE, "PASV %s\r\n", argv[4]);
	if (!send_buff(&ctx, send_msg)) {
		fprintf(stdout, "Failed to read send message\n");
		return 9;
	}
	if (!recv_buff(&ctx, recv_msg, BUFFER_SIZE)) {
		fprintf(stdout, "Failed to read handshake\n");
		return HAND_SHAKE_ERROR;
	}
	
	fprintf(stdout, "%s", recv_msg);
	int ip1, ip2, ip3, ip4, p1, p2;
	int pasv_port;


    // Skip initial digits (227), then everything until first number and then read 6 numbers separated by commas and optional spaces
    if (sscanf(recv_msg, "%*d%*[^0-9]%d , %d , %d , %d , %d , %d",
               &ip1, &ip2, &ip3, &ip4, &p1, &p2) == 6) {
		pasv_port = p1 * 256 + p2;	
		printf("Adress: %d.%d.%d.%d:%d\n", ip1, ip2, ip3, ip4, pasv_port);
    } else {
        fprintf(stderr, "Failed to parse numbers\n");
        return 11;
    }

	SocketContext ptx = {
		.sockfd = -1,
		.max_retries = 3
    };

	if (!create_tcp_socket(&ptx)) {
		fprintf(stdout, "Failed to create TPC socket\n");
		return SOCK_CREATION_ERROR;
	}

	char pasv_host[16];
	snprintf(pasv_host, 16, "%d.%d.%d.%d", ip1, ip2, ip3, ip4);
	if (!connect_to_host(&ptx, pasv_host, pasv_port)) {
		fprintf(stdout, "Failed to connect to host\n");
		return HOST_CONNECTION_ERROR;
	}


	// Close the socket
	// TODO: Catch SIGKILL and similar stuff,
	// then login before killing the app (bash ?)
   	close(ptx.sockfd); 
	close(ctx.sockfd);
    return 0;
}

