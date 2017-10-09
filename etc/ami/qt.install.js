function Controller() {
    installer.autoRejectMessageBoxes();
    installer.installationFinished.connect(function() {
        gui.clickButton(buttons.NextButton);
    })        
}
Controller.prototype.StartMenuDirectoryPageCallback = function() {
    gui.clickButton(buttons.NextButton);
}
Controller.prototype.WelcomePageCallback = function() {
    gui.clickButton(buttons.NextButton);
}
Controller.prototype.CredentialsPageCallback = function() {
    gui.clickButton(buttons.NextButton);
}
Controller.prototype.IntroductionPageCallback = function() {
    gui.clickButton(buttons.NextButton);
}
Controller.prototype.TargetDirectoryPageCallback = function() {
	gui.currentPageWidget().TargetDirectoryLineEdit.setText(installer.value("HomeDir") + "/Qt");
    gui.clickButton(buttons.NextButton);
}
Controller.prototype.ComponentSelectionPageCallback = function() {
    gui.clickButton(buttons.NextButton);    
}
Controller.prototype.LicenseAgreementPageCallback = function() {
    gui.currentPageWidget().AcceptLicenseRadioButton.setChecked(true);
    gui.clickButton(buttons.NextButton);
}
Controller.prototype.ReadyForInstallationPageCallback = function() {	
	gui.clickButton(buttons.CommitButton);
}
Controller.prototype.PerformInstallationPageCallback = function() {	
	gui.clickButton(buttons.CommitButton);
}
Controller.prototype.FinishedPageCallback = function() {	
	gui.clickButton(buttons.CommitButton);
}
