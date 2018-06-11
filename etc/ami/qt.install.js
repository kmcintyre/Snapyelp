function Controller() {
	console.log('yoyo')
    installer.autoRejectMessageBoxes();
    installer.installationFinished.connect(function() {
        gui.clickButton(buttons.NextButton, 3000);
    })        
}
Controller.prototype.StartMenuDirectoryPageCallback = function() {
    gui.clickButton(buttons.NextButton, 3000);
}
Controller.prototype.WelcomePageCallback = function() {
    gui.clickButton(buttons.NextButton, 3000);
}
Controller.prototype.CredentialsPageCallback = function() {
    gui.clickButton(buttons.NextButton, 3000);
}
Controller.prototype.IntroductionPageCallback = function() {
    gui.clickButton(buttons.NextButton, 3000);
}
Controller.prototype.TargetDirectoryPageCallback = function() {
	gui.currentPageWidget().TargetDirectoryLineEdit.setText(installer.value("HomeDir") + "/Qt");
    gui.clickButton(buttons.NextButton, 3000);
}
Controller.prototype.ComponentSelectionPageCallback = function() {
	var widget = gui.currentPageWidget();
	console.log(widget)
	widget.selectAll()
	//console.log('yoyo')
	widget.deselectComponent("qt.qt5.5101.src")
	widget.deselectComponent("qt.qt5.5101.android_armv7")
	widget.deselectComponent("qt.qt5.5101.android_x86")
    gui.clickButton(buttons.NextButton, 3000);    
}
Controller.prototype.LicenseAgreementPageCallback = function() {
    gui.currentPageWidget().AcceptLicenseRadioButton.setChecked(true);
    gui.clickButton(buttons.NextButton, 3000);
}
Controller.prototype.ReadyForInstallationPageCallback = function() {	
	gui.clickButton(buttons.CommitButton, 3000);
}
Controller.prototype.PerformInstallationPageCallback = function() {	
	gui.clickButton(buttons.CommitButton, 3000);
}
Controller.prototype.FinishedPageCallback = function() {	
	gui.clickButton(buttons.CommitButton, 3000);
}