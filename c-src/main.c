#include <stdio.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>

#define BUFFER_SIZE 1024

// Holds socket info and metadata
typedef struct {
    int sockfd;             // file descriptor for the socket
    int max_retries;        // how many times to retry socket creation
    char timestamp[32];     // human-readable timestamp
} SocketContext;


// Fill in current timestamp into the context (e.g. "[28.07.2025 19:21:52]")
void generate_timestamp(SocketContext *pctx) {
    time_t now = time(NULL);                      // get current time (seconds since epoch)
    struct tm *pt = localtime(&now);              // convert to local time (broken-down)
    if (!pt) return;
    strftime(pctx->timestamp, sizeof(pctx->timestamp), "[%d.%m.%Y %H:%M:%S]", pt);  // format it
}


// Check if the file descriptor is valid (>= 0)
int socket_valid(int sockfd) {
	// stdin = 0, stdout = 1, stderr = 2 — those are usually taken,
	// but technically still valid fds
	return sockfd >= 0;
}


// Create a TCP socket, retrying if needed
int create_tcp_socket(SocketContext *pctx) {
    while (pctx->max_retries--) {
        pctx->sockfd = socket(AF_INET, SOCK_STREAM, 0);  // create IPv4 TCP socket
        generate_timestamp(pctx);

        if (socket_valid(pctx->sockfd)) {
            printf("%s Socket created, socketfd->%d\n", pctx->timestamp, pctx->sockfd);
            return 0;
        }

        printf("%s Invalid socketfd->%d\n", pctx->timestamp, pctx->sockfd);
    }

    return -1;  // fail if all retries exhausted
}


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
        printf("%s getaddrinfo: %s\n", pctx->timestamp, gai_strerror(err));
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
		printf("%s Connecting to %s:%d failed\n", pctx->timestamp, host, port);
		return -1;
    }

    generate_timestamp(pctx);
    printf("%s Connected to %s:%d\n", pctx->timestamp, host, port);
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
	printf("%s MSG: %s\n", pctx->timestamp, buffer);
	return 0;
}


int main(int argc, char *argv[]) {
	if (argc < 3) {
        fprintf(stderr, "Usage: %s <server> <port>\n", argv[0]);
        return 1;
    }

	SocketContext ctx = {
		.sockfd = -1,
		.max_retries = 3
    };

	if (create_tcp_socket(&ctx) != 0) {
        fprintf(stderr, "Failed to create socket after retries\n");
        return 1;
    }
	
	char *server = argv[1];
	char *port_str = argv[2];
	int port = atoi(port_str);

	if (connect_to_host(&ctx, server, port) != 0) {
		fprintf(stderr, "Failed to connect to host\n");
		return 1;
	}

	recv_msg(&ctx);

    close(ctx.sockfd);
    return 0;
}

