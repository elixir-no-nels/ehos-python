import { Component, OnInit } from '@angular/core';
import { Node } from '../node';
import { EhosService } from '../ehos.service';


@Component({
  selector: 'app-nodes',
  templateUrl: './nodes.component.html',
  styleUrls: ['./nodes.component.css']
})


export class NodesComponent implements OnInit {
  nodes: Node[];

  constructor(private EhosService: EhosService) { }

  ngOnInit() {
    this.getNodes();
  }

  getNodes(): void {
    this.EhosService.getNodes()
    .subscribe(nodes => this.nodes = nodes);
  }

}
