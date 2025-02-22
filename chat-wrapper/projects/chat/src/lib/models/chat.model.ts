export enum SenderType {
  User,
  Bot,
}

export type Message = {
  id: number;
  sender: SenderType;
  message: string;
};
