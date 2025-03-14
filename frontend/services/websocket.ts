// frontend/services/websocket.ts

type MessageHandler = (data: any) => void;
type ConnectionHandler = () => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string = '';
  private token: string = '';
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private pingInterval: NodeJS.Timeout | null = null;
  private messageHandlers: MessageHandler[] = [];
  private connectHandlers: ConnectionHandler[] = [];
  private disconnectHandlers: ConnectionHandler[] = [];
  private errorHandlers: ((error: Event) => void)[] = [];

  // Create a singleton instance
  private static instance: WebSocketService | null = null;

  public static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  private constructor() {}

  public connect(apiUrl: string, token: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket is already connected');
      return;
    }

    // Use a secure connection if the page is served over HTTPS
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // Get host and port from the API URL
    let url = new URL(apiUrl);
    
    // Construct WebSocket URL
    this.url = `${protocol}//${url.host}`;
    this.token = token;

    try {
      console.log(`Connecting to WebSocket at ${this.url}/api/realtime/ws/${this.token}`);
      this.ws = new WebSocket(`${this.url}/api/realtime/ws/${this.token}`);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.clearTimers();
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  public send(message: any): void {
    if (!this.isConnected()) {
      console.error('WebSocket is not connected. Cannot send message.');
      return;
    }

    this.ws?.send(JSON.stringify(message));
  }

  public addMessageHandler(handler: MessageHandler): void {
    this.messageHandlers.push(handler);
  }

  public removeMessageHandler(handler: MessageHandler): void {
    this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
  }

  public addConnectHandler(handler: ConnectionHandler): void {
    this.connectHandlers.push(handler);
  }

  public removeConnectHandler(handler: ConnectionHandler): void {
    this.connectHandlers = this.connectHandlers.filter(h => h !== handler);
  }

  public addDisconnectHandler(handler: ConnectionHandler): void {
    this.disconnectHandlers.push(handler);
  }

  public removeDisconnectHandler(handler: ConnectionHandler): void {
    this.disconnectHandlers = this.disconnectHandlers.filter(h => h !== handler);
  }

  public addErrorHandler(handler: (error: Event) => void): void {
    this.errorHandlers.push(handler);
  }

  public removeErrorHandler(handler: (error: Event) => void): void {
    this.errorHandlers = this.errorHandlers.filter(h => h !== handler);
  }

  private handleOpen(): void {
    console.log('WebSocket connected');
    
    // Start ping interval to keep connection alive
    this.startPingInterval();
    
    // Notify all connect handlers
    this.connectHandlers.forEach(handler => {
      try {
        handler();
      } catch (error) {
        console.error('Error in connect handler:', error);
      }
    });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      
      // Handle ping-pong internally
      if (data.type === 'pong') {
        console.log('Ping-pong completed');
        return;
      }
      
      // Notify all message handlers
      this.messageHandlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error('Error in message handler:', error);
        }
      });
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error);
    
    // Notify all error handlers
    this.errorHandlers.forEach(handler => {
      try {
        handler(error);
      } catch (err) {
        console.error('Error in error handler:', err);
      }
    });
  }

  private handleClose(): void {
    console.log('WebSocket disconnected');
    
    // Clear timers
    this.clearTimers();
    
    // Attempt to reconnect after a delay
    this.scheduleReconnect();
    
    // Notify all disconnect handlers
    this.disconnectHandlers.forEach(handler => {
      try {
        handler();
      } catch (error) {
        console.error('Error in disconnect handler:', error);
      }
    });
  }

  private startPingInterval(): void {
    // Clear any existing interval
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
    }
    
    // Send a ping every 30 seconds
    this.pingInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping' });
      }
    }, 30000);
  }

  private scheduleReconnect(): void {
    // Clear any existing timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    
    // Try to reconnect after 3 seconds if we have a URL and token
    if (this.url && this.token) {
      this.reconnectTimeout = setTimeout(() => {
        if (document.visibilityState !== 'hidden') {
          console.log('Attempting to reconnect WebSocket...');
          this.connect(this.url, this.token);
        }
      }, 3000);
    }
  }

  private clearTimers(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }
}

export default WebSocketService;