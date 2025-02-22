import { Component } from '@angular/core';
import { ChatComponent } from '../../projects/chat/src/public-api';
import { MarkdownModule } from 'ngx-markdown';
@Component({
  selector: 'app-root',
  imports: [ChatComponent, MarkdownModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'chat-wrapper';
}
