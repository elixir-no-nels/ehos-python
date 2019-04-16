import { Component, OnInit } from '@angular/core';
import { Cloud } from '../cloud';
import { EhosService } from '../ehos.service';


@Component({
  selector: 'app-clouds',
  templateUrl: './clouds.component.html',
  styleUrls: ['./clouds.component.css']
})


export class CloudsComponent implements OnInit {
  clouds: Cloud[];

  constructor(private EhosService: EhosService) { }

  ngOnInit() {
    this.getClouds();
  }

  getClouds(): void {
    this.EhosService.getClouds()
    .subscribe(clouds => this.clouds = clouds);
  }

}

