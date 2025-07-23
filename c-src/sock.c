#include <stdio.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

typedef struct {
    int sockfd;
    int max_retries;
    char timestamp[32];
} SocketContext;

void generate_timestamp(SocketContext *pctx) {
    time_t now = time(NULL);
    struct tm *pt = localtime(&now);
    if (!pt) return;
    strftime(pctx->timestamp, sizeof(pctx->timestamp), "[%d.%m.%Y %H:%M:%S]", pt);
}

int socket_valid(int sockfd) {
    // 0 stdin, 1 stdout, 2 stderr
    // these are common unix file descriptors
    // they may be used but they probably wont be
	return sockfd >= 0;
}

int create_tcp_socket(SocketContext *pctx) {
    while (pctx->max_retries--) {
        pctx->sockfd = socket(AF_INET, SOCK_STREAM, 0);
        generate_timestamp(pctx);

        if (socket_valid(pctx->sockfd)) {
            printf("%s Socket created, socketfd->%d\n", pctx->timestamp, pctx->sockfd);
            return 0;
        }

        printf("%s Invalid socketfd->%d\n", pctx->timestamp, pctx->sockfd);
    }

    return -1;
}

int main() {
    SocketContext ctx = {
        .sockfd = -1,
        .max_retries = 3
    };

    if (create_tcp_socket(&ctx) < 0) {
        fprintf(stderr, "Failed to create socket after retries\n");
        return 1;
    }

    close(ctx.sockfd);
    return 0;
}

