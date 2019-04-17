import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Node } from '../node';
import { State } from '../state';
import { Status } from '../status';
import { EhosService } from '../ehos.service';


@Component({
  selector: 'app-nodes',
  templateUrl: './nodes.component.html',
  styleUrls: ['./nodes.component.css']
})


export class NodesComponent implements OnInit {
  nodes: Node[];
  states: State[];
  status: Status[];
  node_status_id: number;
  node_state_id: number;
  id: number;

  constructor(private EhosService: EhosService,
              private route: ActivatedRoute) { }

  ngOnInit() {
    this.getNodes();
    this.getStatus();
    this.getStates();
  }

  getNodes(): void {

    this.node_status_id = Number(this.route.snapshot.queryParamMap.get("node_status_id"));
    this.node_state_id = Number(this.route.snapshot.queryParamMap.get("node_state_id"));
    this.id = Number(this.route.snapshot.queryParamMap.get('id'));

    console.log( this.id )
    console.log( this.node_state_id )
    console.log( this.node_status_id )

    if ( this.id ) {
      this.EhosService.getNode(this.id).subscribe(nodes => this.nodes = nodes);
    }
    else if ( this.node_state_id) {
      this.EhosService.getNodesByState(this.node_state_id).subscribe(nodes => this.nodes = nodes);
    }
    else if ( this.node_status_id) {
      this.EhosService.getNodesByStatus(this.node_status_id).subscribe(nodes => this.nodes = nodes);
    }
    else {
      this.EhosService.getNodes().subscribe(nodes => this.nodes = nodes);
    }
  }

  getStates(): void {
    this.EhosService.getStates()
      .subscribe(states => this.states = states);
  }

  getStatus(): void {
    this.EhosService.getStatus()
      .subscribe(status => this.status = status);
  }


}
