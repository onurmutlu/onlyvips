declare global {
    interface Window {
      Telegram?: {
        WebApp: {
          ready(): void;
          close(): void;
          initDataUnsafe: {
            user?: {
              id: string;
              username?: string;
              first_name?: string;
            }
          };
          MainButton: {
            show(): void;
            hide(): void;
            setText(text: string): void;
            onClick(callback: () => void): void;
          }
        }
      }
    }
  }
  export {};