import {Component, OnDestroy, OnInit} from '@angular/core';
import {ActivatedRoute, NavigationEnd, Router} from '@angular/router';

import { Node } from '../node';
import { State } from '../state';
import { Status } from '../status';
import { EhosService } from '../ehos.service';


@Component({
  selector: 'app-nodes',
  templateUrl: './nodes.component.html',
  styleUrls: ['./nodes.component.css']
})


export class NodesComponent implements OnInit, OnDestroy {
  nodes: Node[];
  states: State[];
  status: Status[];
  node_status_id: number;
  node_state_id: number;
  id: number;
  navigationSubscription;

  constructor(private EhosService: EhosService,
              private route: ActivatedRoute,
              private router: Router) {

    this.navigationSubscription = this.router.events.subscribe((e: any) => {
      // If it is a NavigationEnd event re-initalise the component
      if (e instanceof NavigationEnd) {
        this.initialiseInvites();
      }
    });
  }

  initialiseInvites() {
    // Set default values and re-fetch any data you need.
    this.getNodes();

  }
  ngOnDestroy() {
    // avoid memory leaks here by cleaning up after ourselves. If we
    // don't then we will continue to run our initialiseInvites()
    // method on every navigationEnd event.
    if (this.navigationSubscription) {
      this.navigationSubscription.unsubscribe();
    }
  }

  ngOnInit() {
    this.getNodes();
    this.getStatus();
    this.getStates();
  }

  getNodes(): void {

    this.node_status_id = Number(this.route.snapshot.queryParamMap.get("node_status_id"));
    this.node_state_id = Number(this.route.snapshot.queryParamMap.get("node_state_id"));
    this.id = Number(this.route.snapshot.queryParamMap.get('id'));

    this.route.queryParams

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
