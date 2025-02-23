import { CommonModule } from '@angular/common';
import { AfterViewChecked, Component, ElementRef, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Message, SenderType } from '../models/chat.model';
import { ChatService } from '../services/chat.service';
import { MarkdownModule } from 'ngx-markdown';
import { ActionKeys, actions } from '../constant/actions';

@Component({
  selector: 'lib-chat',
  imports: [CommonModule, FormsModule, MarkdownModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent implements AfterViewChecked {

  @ViewChild('chatContainer') chatContainer!: ElementRef;
  readonly senderType = SenderType;
  messages: Message[] = [];
  messageText: string = '';
  isChatBotProcessing: boolean = false;
  hasActions: boolean = false;
  chatAction : any = null;
  constructor(private readonly chatService: ChatService) {
    this.messages.push({
      id: this.messages.length,
      sender: SenderType.User,
      message: 'Hello! ',
    });
    this.messages.push({
      id: this.messages.length,
      sender: SenderType.Bot,
      message: 'Hello! How can I help you?',
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom() {
    if (this.chatContainer) {
      this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
    }
  }

  sendMessage() {
    if(this.messageText = "") {
      return;
    }
    this.messages.push({
      id: this.messages.length,
      sender: SenderType.User,
      message: this.messageText,
    });

    this.isChatBotProcessing = true;

    this.chatService.askQuestion(this.messageText).subscribe({
      next: (response: any) => {
        this.messageText = '';
        this.isChatBotProcessing = false;
        this.messages.push({
          id: this.messages.length,
          sender: SenderType.Bot,
          message: response.answer,
        });

        this.scrollToBottom();
      },
      error: (error: any) => {
        this.isChatBotProcessing = false;
        this.messages.push({
          id: this.messages.length,
          sender: SenderType.Bot,
          message: 'Sorry, I am not able to process your request at the moment. Please try again later.',
        });

        this.scrollToBottom();
      }
    });
  }

  getActions(actionKey: ActionKeys) {

    if (actionKey in actions) {
      const actionDetails = actions[actionKey as ActionKeys];
      this.hasActions=true;
      this.chatAction = actionDetails;
      console.log(actionDetails);
    } else {
      console.log("Invalid action key!");
    }
  }
}
