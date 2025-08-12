#include <stdio.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>

#include "structs.h"
#include "sock_utils.h"

int main(int argc, char *argv[]) {
	if (argc < 3) {
        fprintf(stdout, "Usage: %s <server> <port>\n", argv[0]);
        return 1;
    }

	SocketContext ctx = {
		.sockfd = -1,
		.max_retries = 3
    };

	// create master socket
	if (!create_tcp_socket(&ctx)) {
        fprintf(stdout, "Failed to create socket after retries\n");
        return 2;
    }

	// get server and port
	char *server = argv[1];
	char *port_str = argv[2];
	int port = atoi(port_str);

	if (!connect_to_host(&ctx, server, port)) {
		fprintf(stdout, "Failed to connect to host\n");
		return 3;
	}

	// create arrays to store messages
	char send_msg[BUFFER_SIZE];
	char recv_msg[BUFFER_SIZE];
	
	// Read initial response
	if (!recv_buff(&ctx, recv_msg, BUFFER_SIZE)) {
		fprintf(stdout, "Failed to read handshake\n");
		return 4;
	}


	// Send username
	snprintf(send_msg, BUFFER_SIZE, "USER %s\r\n", argv[3]);
	if (!send_buff(&ctx, send_msg)) {
		fprintf(stdout, "Failed to read send message\n");
		return 5;
	}
	if (!recv_buff(&ctx, recv_msg, BUFFER_SIZE)) {
		fprintf(stdout, "Failed to read handshake\n");
		return 4;
	}


	// Send password
	snprintf(send_msg, BUFFER_SIZE, "PASS %s\r\n", argv[4]);
	if (!send_buff(&ctx, send_msg)) {
		fprintf(stdout, "Failed to read send message\n");
		return 7;
	}
	if (!recv_buff(&ctx, recv_msg, BUFFER_SIZE)) {
		fprintf(stdout, "Failed to read handshake\n");
		return 4;
	}

	
	// Enter passive mode
	snprintf(send_msg, BUFFER_SIZE, "PASV %s\r\n", argv[4]);
	if (!send_buff(&ctx, send_msg)) {
		fprintf(stdout, "Failed to read send message\n");
		return 7;
	}
	if (!recv_buff(&ctx, recv_msg, BUFFER_SIZE)) {
		fprintf(stdout, "Failed to read handshake\n");
		return 4;
	}
	// TODO: Parse out PASV response and create PASV socket
	fprintf(stdout, "%s", recv_msg);


	// Close the socket
	// TODO: Catch SIGKILL and similar stuff,
	// then login before killing the app (bash ?)
    close(ctx.sockfd);
    return 0;
}

