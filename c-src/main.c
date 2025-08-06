#include <stdio.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>

#include "structs.h"
#include "sock_utils.h"

#define BUFFER_SIZE 1024

// Connect to given host:port and log result
int connect_to_host(SocketContext *pctx, const char *host, int port) {
    struct addrinfo hints, *pres, *prp;
    char port_str[6];	// port number as string, max "65535"

    snprintf(port_str, sizeof(port_str), "%d", port);  // convert port to string

    memset(&hints, 0, sizeof(hints));	// zero out the hints struct
	hints.ai_family = AF_UNSPEC;		// accept both IPv4 and IPv6
	hints.ai_socktype = SOCK_STREAM;	// TCP stream socket

    int err = getaddrinfo(host, port_str, &hints, &pres);  // resolve host and port
    if (err != 0) {
        generate_timestamp(pctx);
        fprintf(stdout, "%s getaddrinfo: %s\n", pctx->timestamp, gai_strerror(err));
        return -1;
    }

    int connected = 0;
    for (prp = pres; prp != NULL; prp = prp->ai_next) {
        if (connect(pctx->sockfd, prp->ai_addr, prp->ai_addrlen) == 0) {
            connected = 1;
            break;	// success
        }
    }

    freeaddrinfo(pres);	// free linked list of results

    if (!connected) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s Connecting to %s:%d failed\n", pctx->timestamp, host, port);
		return -1;
    }

    generate_timestamp(pctx);
    fprintf(stdout, "%s Connected to %s:%d\n", pctx->timestamp, host, port);
    return 0;
}


int recv_msg(SocketContext *pctx) {
	char buffer[BUFFER_SIZE];
	ssize_t bytes_received;

	// get data from socket
	bytes_received = recv(pctx->sockfd, buffer, BUFFER_SIZE - 1, 0);
	if (bytes_received < 0) {
		generate_timestamp(pctx);
		fprintf(stderr, "%s recv failed !",pctx->timestamp);
		return 1;
	}

	buffer[bytes_received] = '\0';
	generate_timestamp(pctx);
	fprintf(stdout, "%s MSG: %s", pctx->timestamp, buffer);
	return 0;
}


int send_msg(SocketContext *pctx, const char *buffer) {
	// buffer exists	
	if (buffer	== NULL) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s Null Buffer Provided !",pctx->timestamp);
		return 1;
	}

	// buffer is valid size
	size_t num_of_bytes = strnlen(buffer, BUFFER_SIZE);
	if (strlen(buffer) > BUFFER_SIZE) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s buffer exceeds system allowed buffer size !",pctx->timestamp);
		return 1;
	}

	// send buffer
	ssize_t res = send(pctx->sockfd, buffer, num_of_bytes, 0);
	if (res < 0) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s Failed to send data: %s\n", pctx->timestamp, strerror(errno));
		return 1;
	}

	return 0;
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

	if (create_tcp_socket(&ctx) != 0) {
        fprintf(stdout, "Failed to create socket after retries\n");
        return 1;
    }
	
	char *server = argv[1];
	char *port_str = argv[2];
	int port = atoi(port_str);

	if (connect_to_host(&ctx, server, port) != 0) {
		fprintf(stdout, "Failed to connect to host\n");
		return 1;
	}

	if (recv_msg(&ctx) != 0) {
		fprintf(stdout, "Failed to read handshake\n");
		return 1;
	}

	char message[BUFFER_SIZE];
	snprintf(message, BUFFER_SIZE, "USER %s\r\n", argv[3]);
	
	if (send_msg(&ctx, message) != 0) {
		fprintf(stdout, "Failed to read send message\n");
		return 1;
	}

	if (recv_msg(&ctx) != 0) {
		fprintf(stdout, "Failed to read handshake\n");
		return 1;
	}

	snprintf(message, BUFFER_SIZE, "PASS %s\r\n", argv[4]);
	send_msg(&ctx, message);

	if (send_msg(&ctx, message) != 0) {
		fprintf(stdout, "Failed to read send message\n");
		return 1;
	}

	if (recv_msg(&ctx) != 0) {
		fprintf(stdout, "Failed to read handshake\n");
		return 1;
	}

    close(ctx.sockfd);
    return 0;
}

