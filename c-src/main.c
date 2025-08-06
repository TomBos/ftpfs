#include <stdio.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>

#define BUFFER_SIZE 1024

#include "structs.h"
#include "sock_utils.h"


int recv_buff(SocketContext *pctx) {
	char buffer[BUFFER_SIZE];
	ssize_t bytes_received;

	// get data from socket
	bytes_received = recv(pctx->sockfd, buffer, BUFFER_SIZE - 1, 0);
	if (bytes_received < 0) {
		generate_timestamp(pctx);
		fprintf(stderr, "%s recv failed !",pctx->timestamp);
		return 0;
	}

	buffer[bytes_received] = '\0';
	generate_timestamp(pctx);
	fprintf(stdout, "%s MSG: %s", pctx->timestamp, buffer);
	return 1;
}




int main(int argc, char *argv[]) {
	if (argc < 3) {
        fprintf(stdout, "Usage: %s <server> <port>\n", argv[0]);
        return 1;
    }

	SocketContext ctx = {
		.sockfd = -1,
		.max_retries = 3
    };

	if (!create_tcp_socket(&ctx)) {
        fprintf(stdout, "Failed to create socket after retries\n");
        return 2;
    }
	
	char *server = argv[1];
	char *port_str = argv[2];
	int port = atoi(port_str);

	if (!connect_to_host(&ctx, server, port)) {
		fprintf(stdout, "Failed to connect to host\n");
		return 3;
	}

	if (!recv_buff(&ctx)) {
		fprintf(stdout, "Failed to read handshake\n");
		return 4;
	}

	char message[BUFFER_SIZE];
	snprintf(message, BUFFER_SIZE, "USER %s\r\n", argv[3]);
	
	if (!send_buff(&ctx, message)) {
		fprintf(stdout, "Failed to read send message\n");
		return 5;
	}

	if (!recv_buff(&ctx)) {
		fprintf(stdout, "Failed to read handshake\n");
		return 6;
	}

	snprintf(message, BUFFER_SIZE, "PASS %s\r\n", argv[4]);
	send_buff(&ctx, message);

	if (!send_buff(&ctx, message)) {
		fprintf(stdout, "Failed to read send message\n");
		return 7;
	}

	if (!recv_buff(&ctx)) {
		fprintf(stdout, "Failed to read handshake\n");
		return 8;
	}

    close(ctx.sockfd);
    return 0;
}

