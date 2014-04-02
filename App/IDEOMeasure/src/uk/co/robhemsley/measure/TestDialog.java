package uk.co.robhemsley.measure;

import android.app.Dialog;
import android.content.Context;
import android.view.View;
import android.view.Window;

public class TestDialog extends Dialog{

		public TestDialog(Context context, View view) {
	        super(context);
	        requestWindowFeature(Window.FEATURE_NO_TITLE);
	        setContentView(view);
	        getWindow().getDecorView().setBackgroundResource(android.R.color.transparent);
	        getWindow().getAttributes().windowAnimations = R.style.PauseDialogAnimation;
	    }
}
